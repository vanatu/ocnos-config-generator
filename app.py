from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        vendor = request.form.get('vendors')
        hostname = request.form.get('hostname', '')
        
        # Собираем данные интерфейсов
        interfaces = []
        for i in range(5):  # 0 - loopback, 1-4 - интерфейсы
            intf = request.form.get(f'intf{i}', '') if i > 0 else request.form.get('lo', '')
            ip = request.form.get(f'ip{i}', '')
            isis = request.form.get(f'ch-isis_{i}', '') == '1'
            mpls = request.form.get(f'ch-mpls_{i}', '') == '1'
            rsvp = request.form.get(f'ch-rsvp_{i}', '') == '1'
            
            if intf or ip:
                interfaces.append({
                    'name': intf,
                    'ip': ip,
                    'isis': isis,
                    'mpls': mpls,
                    'rsvp': rsvp
                })

        # Генерация конфигурации
        if vendor == 'OcNOS':
            result = generate_ocnos_config(hostname, interfaces)
        elif vendor == 'Junos':
            result = generate_junos_config(hostname, interfaces)
    
    return render_template('index.html', result=result)

def generate_ocnos_config(hostname, interfaces):
    config = []
    intf_cfg = [' ']
    isis_cfg = [' ']
    rsvp_cfg = [' ']
    net = None
    
    if hostname:
        config.append(f"hostname {hostname}")
        config.append("line console 0")
        config.append("exec-timeout 0 0")
        config.append("exit")
        config.append("no ip domain-lookup")
    
    for intf in interfaces:
        if not intf['name']:
            continue
            
        intf_cfg.append(f"interface {intf['name']}")
        
        if intf['ip']:
            if intf['name'].startswith('lo'):
                intf_cfg.append(f"ip address {intf['ip']} secondary")
                net = f"49.0000.0000.{intf['ip'].split('/')[0].split('.')[-1].zfill(4)}.00"
            else:
                intf_cfg.append(f"ip address {intf['ip']}")
        
        if intf['isis']:
            if intf['name'].startswith('lo'):
                isis_cfg.append("router isis 1")
                isis_cfg.append("is-type level-2-only")
                isis_cfg.append(f"net {net}")
                isis_cfg.append(f"passive-interface {intf['name']}")
            else:
                intf_cfg.append("ip router isis 1")
                intf_cfg.append("isis network point-to-point")
        
        if intf['mpls']:
            if not intf['name'].startswith('lo'):
                intf_cfg.append("label-switching")
        
        if intf['rsvp']:
            if not intf['name'].startswith('lo'):
                intf_cfg.append("enable-rsvp")
            else:
                rsvp_cfg.append("router rsvp")
                rsvp_cfg.append("exit")

        intf_cfg.append("exit")
    
    
    return "\n".join(config + isis_cfg + rsvp_cfg + intf_cfg)

def generate_junos_config(hostname, interfaces):
    config = []
    intf_cfg = [' ']
    isis_cfg = [' ']
    mpls_cfg = [' ']
    rsvp_cfg = [' ']
    net = None
    
    if hostname:
        config.append(f"set system host-name {hostname}")
        config.append("set system root-authentication encrypted-password '$1$FdBjSEAv$y9.MbWvwWwISggGWbCraX1'")
    
    for intf in interfaces:
        if not intf['name']:
            continue
            
        if intf['ip']:
            intf_cfg.append(f"set interfaces {intf['name']} unit 0 family inet address {intf['ip']}")
            if intf['name'].startswith('lo'):
                config.append(f"set routing-options router-id {intf['ip'].split('/')[0]}")
                net = f"49.0000.0000.{intf['ip'].split('/')[0].split('.')[-1].zfill(4)}.00"
        
        if intf['isis']:
            if intf['name'].startswith('lo'):
                isis_cfg.append("set protocols isis level 1 disable")
                isis_cfg.append(f"set protocols isis interface {intf['name']} passive")
                intf_cfg.append(f"set interfaces {intf['name']} unit 0 family iso address {net}")
            else:
                isis_cfg.append(f"set protocols isis interface {intf['name']} point-to-point")
                intf_cfg.append(f"set interfaces {intf['name']} unit 0 family iso")
        
        if intf['mpls']:
            if not intf['name'].startswith('lo'):
                intf_cfg.append(f"set interfaces {intf['name']} unit 0 family mpls")
            mpls_cfg.append(f"set protocols mpls interface {intf['name']}")
        
        if intf['rsvp']:
            rsvp_cfg.append(f"set protocols rsvp interface {intf['name']}")
    
    return "\n".join(config + intf_cfg + isis_cfg + mpls_cfg + rsvp_cfg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
