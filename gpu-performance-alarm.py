import json
import boto3
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)
cloudwatch = boto3.client('cloudwatch')

ec2 = boto3.client('ec2')
paginator = ec2.get_paginator('describe_instances')


def setAlarm(instanceID,email,topicArn):
    try:
        cloudwatch.put_metric_alarm(
            AlarmName = instanceID,
            ComparisonOperator='GreaterThanOrEqualToThreshold',
            EvaluationPeriods=1,
            MetricName='CPUUtilization',        
            Namespace='AWS/EC2',
            Period=21600,
            Statistic='Average',
            Threshold=0.0,
            ActionsEnabled=True,
            AlarmActions=[topicArn],
            AlarmDescription='CPU Utilization below 1%',
            Dimensions=[
                {
                  'Name': 'InstanceId',
                  'Value': instanceID
                },
            ]
            #Unit='Seconds'
        )
        print("Alarm Successfully created for "+instanceID)
    except Exception as e:
        print(e)

def get_details(role_arn):
    """
    arn_split = role_arn.split('/')
    assert arn_split[0].endswith("assumed-role")  # Check if arn is of an assumed role
    role_name = arn_split[1]
    session_name = arn_split[2]
    logger.info("{} {}".format(role_name, session_name))
    return role_name, session_name

def createTopic():
    client = boto3.client('sns')
    response = client.create_topic(
        Name='EC2-GPU-Performance-Alarm-Action'
        )
    arn = response['TopicArn']
    return arn

def subscribeTopic(email, topicArn):
    client = boto3.client('sns')
    response = client.subscribe(
        TopicArn=topicArn,
        Protocol='email',
        Endpoint=email,
        ReturnSubscriptionArn=True
        )
    time.sleep(30)
    print(response)
    arn = response['SubscriptionArn']
    return arn
    
def lambda_handler(event, context):
    try:
        #print(str(event).replace("'",'"'))
        role_arn = event['detail']['userIdentity']['arn']
        role_name, session_name = get_details(role_arn)
        if role_name is None or session_name is None:
            return  # Invalid role format and not an IAM User
        #project_name = get_project(role_name)
        topicArn = createTopic()
        email = session_name
        print(email)
       # time.sleep(30)
        subscriptionArn = subscribeTopic(email, topicArn)
        print(subscriptionArn)
        InstanceType = event['detail']['responseElements']['instancesSet']['items'][0]['instanceType']
        print(InstanceType)
        if(InstanceType == "t2.micro"):
            #print("yehi h")
            instanceID = event['detail']['responseElements']['instancesSet']['items'][0]['instanceId']
            print(instanceID)
            setAlarm(instanceID, email, topicArn)
        else:
           # print("ye nhi h")
            

            
    except Exception as e:
        print(e)
    
    
    # response_iterator = paginator.paginate(
    #     Filters=[
    #     {
    #         'Name': 'instance-state-name',
    #         'Values': [
    #             'pending',
    #             'running',
    #             'stopped'
    #         ]
    #     },
    # ],
    # PaginationConfig={'MaxItems': 400}
    # )
    # for n in response_iterator:
    #     for i in n['Reservations']:
    #         for instance in i['Instances']:
    #             print(instance['InstanceId'])
    #             setAlarm(instance['InstanceId'])
            
