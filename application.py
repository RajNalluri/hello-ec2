import base64
import boto3
from flask import Flask, render_template, url_for, request
from flask_restful import Resource, Api
import time

import pdb

IMAGE_ID = 'ami-05fa00d4c63e32376'
INSTANCE_TYPE = 't2.micro'
KEY_NAME = 'my_test_instance'
MIN_COUNT = 1
MAX_COUNT = 1

logged_in_user = None

application = Flask(__name__)
api = Api(application)

class ShowInstances(Resource):
    def get(self):
        ec2 = boto3.client('ec2')
        response = ec2.describe_instances()
        instances = []
        for resrv in response['Reservations']:
            for ins in resrv['Instances']:
                info = {
                    'instance_id': ins['InstanceId'],
                    'instance_state': ins['State']['Name'],
                    'instance_public_dns': ins['PublicDnsName']
                }
                instances.append(info)
        return instances

api.add_resource(ShowInstances, '/api/show_instances')

@application.route('/')
@application.route('/home')
def home():
    return render_template("index.html")

@application.route('/create', methods=['POST', 'GET'])
def create():
    output = request.form.to_dict()
    print(output)
    name = output["name"]
    global logged_in_user
    logged_in_user = name

    return render_template('create.html', name = name)

@application.route('/show', methods=['POST', 'GET'])
def show():
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(
        # Filters=[
        #     # {
        #     #     'Name': 'instance-state-code',
        #     #     'Values': ['16']
        #     # },
        # ]
    )
    instances = []
    for resrv in response['Reservations']:
        for ins in resrv['Instances']:
            info = (ins['InstanceId'], ins['State']['Name'], ins['PublicDnsName'])
            instances.append(info)

    return render_template('show.html', instance_ids = instances)

@application.route('/instance', methods=['POST', 'GET'])
def instance():
    return render_template('instance.html', instance_id = 'instance_id')

@application.route('/status', methods=['POST', 'GET'])
def status():
    user_data = '''
    #!/bin/bash
    echo '
    #   #        #  #          #   #   #          #     #  #
    #   #        #  #          #  # #  #          #     #  #
    #   #   ##   #  #   ##      # # # #   ##   ## #   ###  #
    #####  #  #  #  #  #  #     # # # #  #  #  #  #  #  #  #
    #   #  ####  #  #  #  # ##  # # # #  #  #  #  #  #  #  #
    #   #  #     #  #  #  #     # # # #  #  #  #  #  #  #   
    #   #   ###  #  #   ##       #   #    ##   #  #   ###  #
    ' | sudo tee -a /etc/ssh/my_banner
    echo 'Hello World!' | sudo tee -a /etc/ssh/my_banner
    echo 'Banner /etc/ssh/my_banner' | sudo tee -a /etc/ssh/sshd_config
    sudo systemctl restart sshd.service
    echo '<html><head></head><body><h1>Hello {}!</h1></body></html>' > /tmp/index.html
    cd /tmp/
    sudo python -m SimpleHTTPServer 80
    '''.format(logged_in_user)
    base64_user_data = base64.b64encode(user_data.encode('ascii'))

    ec2 = boto3.resource('ec2')
    result = ec2.create_instances(
        ImageId=IMAGE_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        MinCount=MIN_COUNT,
        MaxCount=MAX_COUNT,
        UserData=base64_user_data,
        TagSpecifications=[
            {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'hello-ec2-{}'.format(time.time())
                },
            ]
        },
        ]
    )
    instance_id = result[0].instance_id
    # instance_id = 'i-0da6f9f607587c1da'

    return render_template('instance.html', instance_id = instance_id)
    
if __name__ == "__main__":
    application.run(debug=True)