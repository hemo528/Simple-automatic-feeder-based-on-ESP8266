import machine
from machine import Pin, PWM
import network
import usocket as socket
import ure
import gc
from machine import SoftI2C
from time import sleep
import ssd1306


i2c = SoftI2C(scl=Pin(5), sda=Pin(4))

# 宽度高度
oled_width = 128
oled_height = 64

# 创建oled屏幕对象
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
# 设置舵机连接的引脚
servo1_pin = 14  # D5口
servo2_pin = 12  # D6口

# 设置PWM频率和占空比范围
pwm_freq = 50
pwm_range = 1000

# 初始化舵机
servo1 = PWM(Pin(servo1_pin), freq=1000, duty=0)
servo2 = PWM(Pin(servo2_pin), freq=1000, duty=0)

# 设置WiFi连接信息
ssid = 'FQ_3'
password = '1223334444@'

# 创建WiFi连接
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

# 等待WiFi连接成功
while not station.isconnected():
    pass

print('Connection successful')
print('IP address:', station.ifconfig()[0])

oled.text(station.ifconfig()[0], 0, 0)
oled.text('Rotating servo1', 0, 10)
oled.text('State : Stop', 0, 20)
oled.text('----------------------', 0, 30)
oled.text('Rotating servo2', 0, 40)
oled.text('State : Stop', 0, 50)
oled.show()
# 定义一个函数，用于控制舵机旋转到指定角度
def rotate_servo(servo, angle):
    # 调整角度范围在 -90 到 90 之间
    angle = max(-90, min(90, angle))
    
    # 计算占空比
    duty = int((angle + 90) / 180 * pwm_range)
    
    # 设置舵机占空比
    servo.duty(duty)




# 处理Web请求的函数
def handle_request(request):
    try:
        print('Handling request:', request)  # 添加调试输出

        if 'rotate_servo1_left' in request:
            print('Rotating servo1 ')
            rotate_servo(servo1, 90)  # 舵机1转
            oled.fill_rect(0, 20, 128, 20, 0)
            oled.show()
            oled.text(station.ifconfig()[0], 0, 0)
            oled.text('Rotating servo1', 0, 10)
            oled.text('State : Start', 0, 20)
            oled.text('----------------------', 0, 30)
            oled.show()
        elif 'rotate_servo1_right' in request:
            print('Rotating servo1 ')
            rotate_servo(servo1, -90) # 舵机1
            oled.fill_rect(0, 20, 128, 20, 0)
            oled.show()
            oled.text(station.ifconfig()[0], 0, 0)
            oled.text('Rotating servo1 left', 0, 10)
            oled.text('State : Stop', 0, 20)
            oled.text('----------------------', 0, 30)
            oled.show()
        elif 'rotate_servo2_up' in request:
            print('Rotating servo2 ')
            rotate_servo(servo2, 90)  # 舵机2
            print('Rotating servo2 ')
            oled.fill_rect(0, 40, 128, 20, 0)
            oled.show()
            oled.text(station.ifconfig()[0], 0, 0)
            oled.text('----------------------', 0, 30)
            oled.text('Rotating servo2', 0, 40)
            oled.text('State : Start', 0, 50)
            oled.show()
        elif 'rotate_servo2_down' in request:
            print('Rotating servo2 down...')
            rotate_servo(servo2, -90) # 舵机2下移
            oled.fill_rect(0, 40, 128, 20, 0)
            oled.show()
            oled.text(station.ifconfig()[0], 0, 0)
            oled.text('----------------------', 0, 30)
            oled.text('Rotating servo2', 0, 40)
            oled.text('State : Stop', 0, 50)
            oled.show()
            
        else:
            print('Unknown command:', request)

    except Exception as e:
        print('Error handling request:', e)

# 创建Web服务器
def serve():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Listening on', addr)

    while True:
        try:
            cl, addr = s.accept()
            print('Client connected from', addr)
            cl_file = cl.makefile('rwb', 0)
            try:
                # 读取请求头
                request_line = cl_file.readline().decode('utf-8').strip()

                # 输出请求头，以便调试
                print('Request Header:', request_line)

                # 使用正则表达式提取参数
                match = ure.search(r'GET /command\?command=([^ ]+)', request_line)
                if match:
                    request = match.group(1)
                    print('Parameter:', request)
                    # 将参数传递给处理函数
                    handle_request(request)
                else:
                    print('Invalid request format')

                # 发送响应
                cl.send("HTTP/1.1 200 OK\r\n")
                cl.send("Content-Type: text/html\r\n\r\n")
                cl.send("<html><body><h1>Control successful!</h1></body></html>")
            except Exception as e:
                print('Error:', e)

            # 关闭连接
            cl.close()
            gc.collect()
        except Exception as e:
            print('Error accepting connection:', e)


# 启动Web服务器
serve()


