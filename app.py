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
            isis = request.form.get(f'check1_{i}', '') == '1'
            mpls = request.form.get(f'check2_{i}', '') == '1'
            rsvp = request.form.get(f'check3_{i}', '') == '1'
            
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
    config.append("enable")
    config.append("configure terminal")
    
    if hostname:
        config.append(f"hostname {hostname}")
    
    config.append("line console 0")
    config.append("exec-timeout 0 0")
    config.append("exit")
    config.append("no ip domain-lookup")
    
    for intf in interfaces:
        if not intf['name']:
            continue
            
        config.append(f"interface {intf['name']}")
        
        if intf['ip']:
            config.append(f"ip address {intf['ip']}")
        
        if intf['isis']:
            config.append("ip router isis")
        
        if intf['mpls']:
            config.append("mpls ip")
        
        if intf['rsvp']:
            config.append("mpls rsvp-te")
        
        config.append("no shutdown")
        config.append("exit")
    
    config.append("end")
    config.append("write memory")
    
    return "\n".join(config)

def generate_junos_config(hostname, interfaces):
    config = []
    config.append("set system root-authentication encrypted-password '$1$FdBjSEAv$y9.MbWvwWwISggGWbCraX1'")
    
    if hostname:
        config.append(f"set system host-name {hostname}")
    
    for intf in interfaces:
        if not intf['name']:
            continue
            
        if intf['ip']:
            config.append(f"set interfaces {intf['name']} unit 0 family inet address {intf['ip']}")
        
        if intf['isis']:
            config.append(f"set protocols isis interface {intf['name']}")
        
        if intf['mpls']:
            config.append(f"set protocols mpls interface {intf['name']}")
        
        if intf['rsvp']:
            config.append(f"set protocols rsvp interface {intf['name']}")
    
    return "\n".join(config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)