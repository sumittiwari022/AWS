
import boto3
import traceback

ec2 = boto3.client('ec2')
rds = boto3.client('rds')

def lambda_handler(event, context):

    try:
        start_stop_ec2_instances(event, context)
       
        start_stop_rds_instances(event, context)
       
        return "Completed"
       
    except Exception as e:
            displayException(e)
            traceback.print_exc()
           
def start_stop_ec2_instances(event, context):
    
    # Get action parameter from event
    action = event.get('action')
    
    if action is None:
        action = ''

    # Check action
    if action.lower() not in ['start', 'stop']:
        print ("action was neither start nor stop. start_stop_ec2_instances() aborted.")
    else:
        # Get ec2 instances which match filter conditions
        filtered_ec2 = ec2.describe_instances(
            Filters=[
                #{'Name': 'tag-key', 'Values': ['Auto-StartStop-Enabled', 'auto-startstop-enabled']},
                {'Name': 'tag:schedule','Values': ['nine-to-six']},
                {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
            ]
        ).get(
            'Reservations', []
        )
    
        # Convert array of array to a flat array
        instances_ec2 = sum(
            [
                [i for i in r['Instances']]
                for r in filtered_ec2
            ], [])
    
        print ("Found " + str(len(instances_ec2)) + " EC2 instances that can be started/stopped")
    
        # Loop through instances
        for instance_ec2 in instances_ec2:

            try:
                instance_id = instance_ec2['InstanceId']

                # Get ec2 instance name tag
                for tag in instance_ec2['Tags']:
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                        print ("instance_name: " + instance_name + " instance_id: " + instance_id)
                        continue
                    
                # Get ec2 instance current status
                instance_state = instance_ec2['State']['Name']
                print ("Current instance_state: %s" % instance_state)
                
                # Start or stop ec2 instance
                if instance_state == 'running' and action == 'stop':
                    ec2.stop_instances(
                        InstanceIds=[
                            instance_id
                            ],
                        # DryRun = True
                        )
                    print ("Instance %s comes to stop" % instance_id)
                    
                elif instance_state == 'stopped' and action == 'start':
                    ec2.start_instances(
                        InstanceIds=[
                            instance_id
                            ],
                        # DryRun = True
                        )
                    print ("Instance %s comes to start" % instance_id)
                    
                else:
                    print ("Instance %s(%s) status is not right to start or stop" % (instance_id, instance_name))
                
            except Exception as e:
                displayException(e)
                # traceback.print_exc()



# Caution: RDS instance will be started by AWS automatically after it is down for 7 days. Adjust cronjob in CloudWatch if you want to stop it again after 7 days.
def start_stop_rds_instances(event, context):

    # Get action parameter from event
    action = event.get('action')

    # Check action
    if action is None:
        action = ''

    if action.lower() not in ['start', 'stop']:
        print ("action was neither start nor stop. start_stop_rds_instances() aborted.")
    else:
        #===========================================
        # For MySQL, MariaDB, PostgreSQL and Oracle
        #===========================================

        # Get all of rds instances
        instances_rds = rds.describe_db_instances().get('DBInstances', [])

        # Loop through instances
        for instance_rds in instances_rds:

            try:
                if instance_rds['Engine'] in ['mysql', 'mariadb', 'postgres'] or 'oracle' in instance_rds['Engine']:

                    # Get rds instance tags
                    tags = rds.list_tags_for_resource(ResourceName = instance_rds['DBInstanceArn']).get('TagList',[])
                   
                    for tag in tags:
           
                        if tag['Key'] == 'schedule' and tag['Value'] == 'nine-to-six':
                        #if (tag['Values'] == 'prod_hours'):
           
                            instanceState = instance_rds['DBInstanceStatus']

                            # Start or stop instance
                            if instanceState == 'available' and action == 'stop':

                                print ("Found instance " + instance_rds['DBInstanceIdentifier'] + " that can be stopped")
                               
                                rds.stop_db_instance(
                                    DBInstanceIdentifier = instance_rds['DBInstanceIdentifier']
                                )
                                print ("Instance %s stopped" % instance_rds['DBInstanceIdentifier'])
                               
                       
                            elif instanceState == 'stopped' and action == 'start':
                                   
                                print ("Found instance " + instance_rds['DBInstanceIdentifier'] + " that can be started")
                               
                                rds.start_db_instance(
                                    DBInstanceIdentifier = instance_rds['DBInstanceIdentifier']
                                )
                                print ("Instance %s started" % instance_rds['DBInstanceIdentifier'])
                               
                            else:
                                print ("Current status of %s is %s. It is not a right status for starting or stopping." % (instance_rds['DBInstanceIdentifier'], instanceState))
                           
            except Exception as e:
                displayException(e)
                # traceback.print_exc()


        #=================
        # For AWS Aurora
        #=================
        # Notes: 1. Auto-StartStop-Enabled tag should be applied on cluster, not on instance
        # Notes: 2. Make sure StartDBCluster and StopDBCluster services are attached to IAM role

        # Get all of rds clusters
        clusters_rds = rds.describe_db_clusters().get('DBClusters', [])
       
        for cluster_rds in clusters_rds:

            try:
                if 'aurora' in cluster_rds['Engine']:
                   
                    # Get rds instance tags
                    tags = rds.list_tags_for_resource(ResourceName = cluster_rds['DBClusterArn']).get('TagList',[])

                    for tag in tags:
           
                        #if tag['Key'] == 'Auto-StartStop-Enabled':
                        if tag['Key'] == 'schedule' and tag['Value'] == 'nine-to-six':
                        #if (tag['Values'] == 'prod_hours'):
                           
                            clusterState = cluster_rds['Status']

                            # Start or stop instance
                            if clusterState == 'available' and action == 'stop':

                                print ("Found cluster " + cluster_rds['DBClusterIdentifier'] + " that can be stopped")
                               
                                rds.stop_db_cluster(
                                    DBClusterIdentifier = cluster_rds['DBClusterIdentifier']
                                )
                                print ("Cluster %s stopped" % cluster_rds['DBClusterIdentifier'])
                               
                       
                            elif clusterState == 'stopped' and action == 'start':
                                   
                                print ("Found cluster " + cluster_rds['DBClusterIdentifier'] + " that can be started")
                               
                                rds.start_db_cluster(
                                    DBClusterIdentifier = cluster_rds['DBClusterIdentifier']
                                )
                                print ("Cluster %s started" % cluster_rds['DBClusterIdentifier'])
                               
                            else:
                                print ("Current status of %s is %s. It is not a right status for starting or stopping." % (cluster_rds['DBClusterIdentifier'], instanceState))
                           
            except Exception as e:
                displayException(e)
                # traceback.print_exc()
           

def displayException(exception):
    exception_type = exception.__class__.__name__
    exception_message = str(exception)

    print("Exception type: %s; Exception message: %s;" % (exception_type, exception_message))
