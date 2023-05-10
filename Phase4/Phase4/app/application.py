#pytorch
#cmd installations
#pip install pydash
#pip install dash_daq
#sudo apt-get remove thonny
#sudo apt-get install thonny
#pip install dash-bootstrap-components
#pip install dash_mqtt
#pip install paho-mqtt

import dash.dependencies
import dash_daq as daq
from dash import html, Input, Output, dcc, Dash, State
import dash_bootstrap_components as dbc
import RPi.GPIO as GPIO
import Freenove_DHT as DHT
import time as time
import smtplib
import email
import imaplib
import dash_mqtt
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sqlite3

is_sent = True

Motor1 = 15 # Enable Pin | 22 board
Motor2 = 13 # Input Pin  | 27 board
Motor3 = 11 # Input Pin  | 17 board
#setup GPIO outputs
lightpin = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(lightpin, GPIO.OUT)
lightsensor = 0
LEDStatus = False
hasLEDEmailSent = False
humi = 0
temp = 0

RFID = ''
name = ''
humipref = 9999
temppref = 9999
lightpref = 0


DHTPin = 40 #define the pin of DHT11
dht = DHT.DHT(DHTPin) #create a DHT class object

# def get_both(): 
#     global is_sent   
#     #for i in range(0,15):
#     #    chk = dht.readDHT11() #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
#     #    if (chk is dht.DHTLIB_OK): #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
#     #        print("DHT11,OK!")
#     #        break
#     #    time.sleep(0.1)
#     chk = dht.readDHT11()
#     humi = dht.humidity
#     temp = dht.temperature
#     if (temp >= 24 and is_sent):
#         send_email(temp)   
#         is_sent = False
#     receive_reply()
#     humi = '{0:0.1f}'.format(humi)
#     temp = '{0:0.1f}'.format(temp)
#     print(humi)
#     print(temp)
#     #time.sleep(5)
#     return temp, humi

def motor_on():
    global Motor1 # Enable Pin | 22 board
    global Motor2 # Input Pin  | 27 board
    global Motor3 # Input Pin  | 17 board
    GPIO.setup(Motor1,GPIO.OUT)
    GPIO.setup(Motor2,GPIO.OUT)
    GPIO.setup(Motor3,GPIO.OUT)

    GPIO.output(Motor1,GPIO.HIGH)
    GPIO.output(Motor2,GPIO.LOW)
    GPIO.output(Motor3,GPIO.HIGH)
    
def send_email(temp):
    
    # Set up the email addresses and password
    my_address = "iotburner28@gmail.com" # Replace with your own Gmail address
    my_password = "uefa acwp roct hnuc" # Replace with your Gmail password
    recipient_address = "ilikefortniteseason4@gmail.com" # Replace with the recipient's email address

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = my_address
    msg['To'] = recipient_address
    msg['Subject'] = "IoT Fan"

    # Add the body to the email
    body = "The current temperature is " + str(temp) + ". Would you like to turn on the fan?"
    msg.attach(MIMEText(body, 'plain'))
     
    # Log in to the Gmail SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(my_address, my_password)

    # Send the email
    text = msg.as_string()
    server.sendmail(my_address, recipient_address, text)

    # Log out of the server
    print('sent to ' + recipient_address)
    server.quit()

def useremail(user):
    # Set up the email addresses and password
    my_address = "iotburner28@gmail.com" # Replace with your own Gmail address
    my_password = "uefa acwp roct hnuc" # Replace with your Gmail password
    recipient_address = "ilikefortniteseason4@gmail.com" # Replace with the recipient's email address

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = my_address
    msg['To'] = recipient_address
    msg['Subject'] = "User Sign in"

    # Add the body to the email
    body = f"Welcome, {user}!"
    msg.attach(MIMEText(body, 'plain'))
     
    # Log in to the Gmail SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(my_address, my_password)

    # Send the email
    text = msg.as_string()
    server.sendmail(my_address, recipient_address, text)

    # Log out of the server
    print('sent to ' + recipient_address)
    server.quit()
    
def receive_reply():
    EMAIL = "iotburner28@gmail.com" # Replace with your own Gmail address
    PASSWORD = "uefa acwp roct hnuc" # Replace with your Gmail password
    SERVER = "imap.gmail.com"

    # connect to the server and go to its inbox
    mail = imaplib.IMAP4_SSL(SERVER)
    mail.login(EMAIL, PASSWORD)

    mail.select('inbox')
    status, data = mail.search(None, 'ALL')
    mail_ids = []

    for block in data:
        mail_ids += block.split()

    for i in mail_ids:
        status, data = mail.fetch(i, '(RFC822)')

        for response_part in data:
            if isinstance(response_part, tuple):
                message = email.message_from_bytes(response_part[1])

                mail_from = message['from']
                mail_subject = message['subject']

                if message.is_multipart():
                    mail_content = ''

                    for part in message.get_payload():
                        if part.get_content_type() == 'text/plain':
                            mail_content += part.get_payload()
                else:
                    mail_content = message.get_payload()

                if mail_content == 'yes' or 'yes' in mail_subject.lower() or any('yes' in recipient.lower() for recipient in message.get_all('to', [])) or 'yes' in mail_content.lower():
                    print(f'From: {mail_from}')
                    print(f'Subject: {mail_subject}')
                    print(f'Content: {mail_content}')
                    #can start motor
                    motor_on()
                    
def on_message(client, userdata, msg):
    global hasLEDEmailSent
    global is_sent
    global lightsensor
    global LEDStatus
    global temp
    global humi
    global RFID
    global temppref
    global humipref
    global lightpref
    
    date = time.strftime('%d/%m/%Y %H:%M:%S')
    print(msg.payload.decode("utf-8"))
    print(msg.topic)
    
    if('photoValue' in msg.topic):
        lightsensor = float(msg.payload.decode("utf-8"))
        print(lightsensor + float(0))
        
        if (lightsensor <= lightpref) and (hasLEDEmailSent is False):
            current_time = datetime.now().strftime("%H:%M")
            light_email(current_time)
            hasLEDEmailSent = True
            LEDStatus = True
            time.sleep(3)
            print(LEDStatus)
        else:
            LEDStatus = False
            print(LEDStatus)
                
    if ('humidity1' in msg.topic):
        humi = float(msg.payload.decode("utf-8"))
    if ('temperature1' in msg.topic):
        temp = float(msg.payload.decode("utf-8"))
    if ('RFID' in msg.topic):
        RFID = str(msg.payload.decode("utf-8"))
        on_rfid_scanned(RFID)
        
    print("Humidity:", humi)
    print("RFID:", RFID)
    print("Temperature:", temp)
        
    if (temp >= temppref and is_sent):
        send_email(temp)
        is_sent = False
        receive_reply()
    

# def database():
#     global temppref
#     global humipref
#     global lightpref
#     global RFID
#     global name
#     # Connect to SQLite database
#     conn = sqlite3.connect('/home/pi/Desktop/IoTFinalProject-main/Phase4/app/data/users.db')
#     c = conn.cursor()
# 
#     # Retrieve user data associated with RFID tag ID
#     c.execute('SELECT * FROM users WHERE user_id = ?', (RFID,))
#     user_data = c.fetchone()
#     print("User data:", user_data)
# 
#     # Retrieve temperature, humidity, and light intensity values from user data
#     RFID = user_data[0]
#     name = user_data[1]
#     temppref = user_data[2]
#     humipref = user_data[3]
#     lightpref = user_data[4]
# 
#     # Close database connection
#     conn.close()
#     
#     return user_data
    
def get_user_data(RFID):
    
    # Connect to the database
    conn = sqlite3.connect('/home/pi/Desktop/IoTFinalProject-main/Phase4/app/data/users.db')
    c = conn.cursor()

    # Execute the SQL query to get the user data
    c.execute("SELECT * FROM users WHERE user_id=?", (RFID,))
    user_data = c.fetchone()

    # Close the database connection
    conn.close()
    
        # Format the user data as a dictionary
    if user_data:
        #useremail(user_data[1])
        print(user_data[1])
        return user_data#dict
    else:
        return None

    #return user_data

def on_rfid_scanned(RFID):
    global temppref
    global humipref
    global lightpref
    #global RFID
    global name
    user_data = get_user_data(RFID)
    if user_data:
        print("User data:", user_data)
        # Do something with the user data
        RFID = user_data[0]
        name = user_data[1]
        temppref = user_data[2]
        humipref = user_data[3]
        lightpref = user_data[4]
        print(lightpref)
    else:
        print("User not found in database")
        
        
def light_email(current_time):
# Set up the email addresses and password
    my_address = "iotburner28@gmail.com" # Replace with your own Gmail address
    my_password = "uefa acwp roct hnuc" # Replace with your Gmail password
    recipient_address = "ilikefortniteseason4@gmail.com" # Replace with the recipient's email address
    print("method was called")
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = my_address
    msg['To'] = recipient_address
    msg['Subject'] = "IoT Lightsensor"

    # Add the body to the email
    body = f"The Light is ON at {current_time}."
    msg.attach(MIMEText(body, 'plain'))

    # Log in to the Gmail SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(my_address, my_password)

    # Send the email
    text = msg.as_string()
    server.sendmail(my_address, recipient_address, text)

    # Log out of the server
    print('sent to ' + recipient_address)
    server.quit()
    
    # Publish a message to a topic that the dashboard is subscribed to
    publish.single("dashboard/message", "Email has been sent", hostname="localhost")
            
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("IoTlab/photoValue")
    client.subscribe("vanieriot/photoValue1")
    client.subscribe("vanieriot/temperature1")
    client.subscribe("vanieriot/humidity1")
    client.subscribe("vanieriot/RFID")
    

#initialize app
app = Dash(__name__)

on_image = app.get_asset_url('on.png')
off_image = app.get_asset_url('off.png')
initial_image = on_image if LEDStatus else off_image

@app.callback(
    Output('light-image', 'src'),
    Input('interval-component', 'n_intervals'),
    State('light-image', 'src'))

def update_image(n, src):
    # Update LED image
    new_image = on_image if LEDStatus else off_image
    if new_image != src:
        return new_image
    else:
        return dash.no_update

    
#dashboard layout
def htmlstructure():
    global name
    return html.Div([
            html.H1(children='Control Panel', style={'text-align': 'center', 'font-size': '300%'}),
        #     
        #     html.Div([
        #         html.H1('User Data'),
        #         dcc.Input(id='rfid-input', type='text', placeholder='Enter RFID value'),
        #         html.Div(id='user-data')
        #     ]),
        #
         
            html.Div(className='sidebar',
                     id="user-info",
                     children=[
                     ]),   
            
            
        #     html.Div([
        #         html.H1(f"Welcome {name}!"),
        #         html.Span(':{}'.format(name))
        #         # add more dashboard elements here
        #     ]),
            
          
            html.Div(
            [
                dcc.Graph(
                    id="temp-gauge",
                    figure={
                        "data": [
                            {
                                "type": "indicator",
                                "value": temp,
                                "mode": "gauge+number",
                                "title": {"text": "Temperature"},
                                "gauge": {
                                    "axis": {"range": [None, 50]},
                                    "bar": {"color": "#f44336"},
                                    "threshold": {
                                        "line": {"color": "black", "width": 4},
                                        "thickness": 0.75,
                                        "value": 35,
                                    },
                                    "steps": [
                                        {"range": [0, 10], "color": "rgb(242, 242, 242)"},
                                        {"range": [10, 20], "color": "rgb(217, 217, 217)"},
                                        {"range": [20, 30], "color": "rgb(191, 191, 191)"},
                                        {"range": [30, 40], "color": "rgb(166, 166, 166)"},
                                        {"range": [40, 50], "color": "rgb(140, 140, 140)"},
                                    ],
                                    "borderwidth": 2,
                                    "bordercolor": "#b0bec5",
                                    "height": 100,  # Set the height of the gauge to 150 pixels
                                    "width": 100,  # Set the width of the gauge to 150 pixels
                                },
                            }
                        ]
                    },
                    style={"width": "30%", "display": "inline-block"},
                ),
                
               dcc.Graph(
                id="humi-gauge",
                figure={
                    "data": [
                        {
                            "type": "indicator",
                            "value": humi,
                            "mode": "gauge+number",
                            "title": {"text": "Humidity"},
                            "gauge": {
                                "axis": {"range": [None, 100]},
                                "bar": {"color": "#2196f3"},
                                "threshold": {
                                    "line": {"color": "black", "width": 4},
                                    "thickness": 0.75,
                                    "value": 70,
                                },
                                "steps": [
                                    {"range": [0, 20], "color": "#e1f5fe"},
                                    {"range": [20, 40], "color": "#b3e5fc"},
                                    {"range": [40, 60], "color": "#81d4fa"},
                                    {"range": [60, 80], "color": "#4fc3f7"},
                                    {"range": [80, 100], "color": "#29b6f6"},
                                ],
                                "borderwidth": 2,
                                "bordercolor": "#b0bec5",
                                "bgcolor": "rgba(0,0,0,0)",
                            },
                        }
                    ]
                },
                style={"width": "30%", "display": "inline-block"},
            ),
                
              dcc.Graph(
                id="light-gauge",
                figure={
                    "data": [
                        {
                            "type": "indicator",
                            "value": lightsensor,
                            "mode": "gauge+number",
                            "title": {"text": "Light Intensity"},
                            "gauge": {
                                "axis": {"range": [None, 1000]},
                                "bar": {"color": "yellow"},  # change bar color to yellow
                                "threshold": {
                                    "line": {"color": "black", "width": 4},
                                    "thickness": 0.75,
                                    "value": 35,
                                },
                                "steps": [
                                    {"range": [0, 200], "color": "#fff9c4"},  # change step color to pale yellow
                                    {"range": [200, 400], "color": "#fff59d"},
                                    {"range": [400, 600], "color": "#fff176"},
                                    {"range": [600, 800], "color": "#ffee58"},
                                    {"range": [800, 1000], "color": "#ffeb3b"},
                                ],
                                "borderwidth": 2,
                                "bordercolor": "#b0bec5",
                        },
                    }
                ]
            },
            style={"width": "30%", "display": "inline-block"},
        )
                
            ],
            style={"text-align": "center"},
        ),
          html.Div(
           style={'text-align': 'center'},
            children=[
                html.Div([
                    html.H1("Email Status"),
                    html.Div(
                        id="email-status",
                        children="Email not yet sent",
                        style={'font-size': '24px'}  # add font size style
                    )
                ], style={'display': 'inline-block'}),
                
                html.Div([

                ], style={'display': 'inline-block'}),
                
                html.Div([
                    html.H1("Light Status"),
                    html.Img(id='light-image', src=initial_image, height=200, width=200),
                ], style={'display': 'inline-block'}),

                html.Div([
                    html.H1("Fan Status"),
                    html.Img(id='fan-image', src=app.get_asset_url("fan.png"), height=200, width=200),
                ], style={'display': 'inline-block'}),
            ]
        ),
            dcc.Interval(
                id='interval-component',
                interval=2 * 1000,  # updates every 2 seconds
                n_intervals=0
            )
        ], style={'font-size': '15px'})


#@app.callback(Output('user-data', 'children'), [Input('rfid-input', 'value')])
# def update_user_data(RFID):
#     if not RFID:
#         return "Please enter an RFID value"
#     user_data = get_user_data(RFID)
#     if user_data:
#         # format the user data as plain text
#         user_data_text = f"User data:\nUser_ID: {user_data['user_id']}\nName: {user_data['name']}\nTemperature: {user_data['temperature']}\nHumidity: {user_data['humidity']}\nLight_Intensity: {user_data['light_intensity']}"
#         return user_data_text
#     else:
#         return "User not found in database"

app.title = 'Phase 4'
app.layout = htmlstructure()

# create a callback function that updates the email status text
@app.callback(
    Output("email-status", "children"),
    [Input("interval-component", "n_intervals")],
)
def update_email_status(n):
    global hasLEDEmailSent
    
    if hasLEDEmailSent:
        return "Email has been sent"
    else:
        return "Email not yet sent"

# create an interval component that updates every 5 seconds
@app.callback(Output("interval-component", "interval"), [Input("interval-component", "n_intervals")])
def update_interval(n):
    return 5 * 1000

@app.callback(Output("user-info", "children"), [Input("interval-component", "n_intervals")])
def update_user(n):
    global name
    global humipref
    global temppref
    global lightpref
    print(str(humipref) + "Anything else")
    return html.Div([html.H1('Welcome, {}'.format(str(name)) if str(name) else 'Welcome, Unknown User'), html.Br(),
                     html.H2('Your prefered humidity is {}'.format(str(humipref)) if str(humipref) else 'Unknown Humidity Preference'), html.Br(),
                     html.H2('Your prefered temperature is {}'.format(str(temppref)) if str(temppref) else 'Unknown Temperature Preference'), html.Br(),
                     html.H2('Your prefered light intesity is {}'.format(str(lightpref)) if str(lightpref) else 'Unknown Light Preference')
                     ])

# create a function that updates hasLEDEmailSent
def update_email_sent_status():
    global hasLEDEmailSent
    
    # do some check to update hasLEDEmailSent
    hasLEDEmailSent = True


@app.callback(
    Output("temp-gauge", "figure"),
    Output("humi-gauge", "figure"),
    Output("light-gauge", "figure"),
    Input('interval-component', 'n_intervals')
)
def update_gauges(n):
    global temp, humi, lightsensor
    
    temp_fig = {
        "data": [
            {
                "type": "indicator",
                "value": temp,
                "mode": "gauge+number",
                "title": {"text": "Temperature"},
                "gauge": {
                    "axis": {"range": [None, 50]},
                    "bar": {"color": "#f44336"},
                    "threshold": {
                        "line": {"color": "black", "width": 4},
                        "thickness": 0.75,
                        "value": 35,
                    },
                    "steps": [
                        {"range": [0, 10], "color": "rgb(242, 242, 242)"},
                        {"range": [10, 20], "color": "rgb(217, 217, 217)"},
                        {"range": [20, 30], "color": "rgb(191, 191, 191)"},
                        {"range": [30, 40], "color": "rgb(166, 166, 166)"},
                        {"range": [40, 50], "color": "rgb(140, 140, 140)"},
                    ],
                    "borderwidth": 2,
                    "bordercolor": "#b0bec5",
                    "height": 100,  # Set the height of the gauge to 150 pixels
                    "width": 100,  # Set the width of the gauge to 150 pixels
                },
            }
        ]
    }
    
    humi_fig = {
        "data": [
                {
                    "type": "indicator",
                    "value": humi,
                    "mode": "gauge+number",
                    "title": {"text": "Humidity"},
                    "gauge": {
                        "axis": {"range": [None, 100]},
                        "bar": {"color": "#2196f3"},
                        "threshold": {
                            "line": {"color": "black", "width": 4},
                            "thickness": 0.75,
                            "value": 70,
                        },
                        "steps": [
                            {"range": [0, 20], "color": "#e1f5fe"},
                            {"range": [20, 40], "color": "#b3e5fc"},
                            {"range": [40, 60], "color": "#81d4fa"},
                            {"range": [60, 80], "color": "#4fc3f7"},
                            {"range": [80, 100], "color": "#29b6f6"},
                        ],
                        "borderwidth": 2,
                        "bordercolor": "#b0bec5",
                        "bgcolor": "rgba(0,0,0,0)",
                },
            }
        ]
    }
    
    light_fig = {
        "data": [
                {
                    "type": "indicator",
                    "value": lightsensor,
                    "mode": "gauge+number",
                    "title": {"text": "Light Intensity"},
                    "gauge": {
                        "axis": {"range": [None, 1000]},
                        "bar": {"color": "yellow"},  # change bar color to yellow
                        "threshold": {
                            "line": {"color": "black", "width": 4},
                            "thickness": 0.75,
                            "value": 35,
                        },
                        "steps": [
                            {"range": [0, 200], "color": "#fff9c4"},  # change step color to pale yellow
                            {"range": [200, 400], "color": "#fff59d"},
                            {"range": [400, 600], "color": "#fff176"},
                            {"range": [600, 800], "color": "#ffee58"},
                            {"range": [800, 1000], "color": "#ffeb3b"},
                        ],
                        "borderwidth": 2,
                        "bordercolor": "#b0bec5",
                },
            }
        ]
    }
    
    return temp_fig, humi_fig, light_fig

# def update_values(n):
#     temp, humi = get_both()
#     return f'Temperature: {temp} C', f'Humidity: {humi}%'
#

# @app.callback(
#     Output('led-img', 'children'),
#     Input('led-img', 'n_clicks')
# )

#function to control the button on the dashboard
# def control_output(n_clicks):
#     #check if n_clicks is 1 or 0
#     if n_clicks % 2 == 1:
#         print(n_clicks % 2)
#         #turns off light
#         GPIO.output(lightpin, GPIO.LOW)
#         #returns updated img
#         return html.Img(src=app.get_asset_url('off.png'),width='200px', height='200px')
#     else:
#         print(n_clicks % 2)
#         #turns on light
#         GPIO.output(lightpin, GPIO.HIGH)
#         return html.Img(src=app.get_asset_url('on.png'),width='200px', height='200px')
    
# Define the callback function for the button
@app.callback(
    Output('output', 'children'),
    Input('button', 'n_clicks')
)
def update_output(n_clicks):
    if n_clicks % 2 == 1:
        print(n_clicks % 2)
        #turns off motor
        GPIO.output(Motor1,GPIO.LOW)
        #returns updated img
        return ''
    else:
        print(n_clicks % 2)
        #turns on motor
        motor_on()
        return ''

#runs server
if __name__ == '__main__':
    print ('Program is starting ... ')
    client = mqtt.Client()
    client.connect("0.0.0.0", 1883)
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_start()
    app.run_server(debug=True) 
