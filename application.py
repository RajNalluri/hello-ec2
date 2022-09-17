import base64
import boto3
from flask import Flask, render_template, url_for, request

import pdb

IMAGE_ID = 'ami-05fa00d4c63e32376'
INSTANCE_TYPE = 't2.micro'
KEY_NAME = 'my_test_instance'
MIN_COUNT = 1
MAX_COUNT = 1

application = Flask(__name__)

@application.route('/')
@application.route('/home')
def home():
    return render_template("index.html")

@application.route('/create', methods=['POST', 'GET'])
def create():
    output = request.form.to_dict()
    print(output)
    name = output["name"]

    return render_template('create.html', name = name)

@application.route('/instance', methods=['POST', 'GET'])
def instance():
    return render_template('instance.html', instance_id = 'instance_id')

@application.route('/status', methods=['POST', 'GET'])
def status():
    # output = request.form.to_dict()
    # print(output)
    # name = output["name"]

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
    echo 'Hello World!' > /tmp/hello.txt
    '''
    # user_data = 'echo Hello {}'.format(name)
    base64_user_data = base64.b64encode(user_data.encode('ascii'))

    ec2 = boto3.resource('ec2')
    result = ec2.create_instances(
    ImageId=IMAGE_ID,
    InstanceType=INSTANCE_TYPE,
    KeyName=KEY_NAME,
    MinCount=MIN_COUNT,
    MaxCount=MAX_COUNT,
    UserData=base64_user_data
    )

    instance_id = result[0]

    return render_template('instance.html', instance_id = instance_id)
    
if __name__ == "__main__":
    application.run(debug=True)