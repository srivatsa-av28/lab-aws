#!/usr/bin/env python3
"""
Script to shut down AWS EC2 instances older than 24 hours.
Looks for instances with the 'AutoShutdown' tag set to 'true'.
"""

import boto3
from datetime import datetime, timezone, timedelta
import sys

def get_old_instances(ec2_client, hours=24):
    """Get instances older than specified hours with AutoShutdown tag."""
    
    # Calculate cutoff time
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # Get all running instances with AutoShutdown tag
    response = ec2_client.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': 'tag:AutoShutdown', 'Values': ['true']}
        ]
    )
    
    old_instances = []
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            launch_time = instance['LaunchTime']
            
            # Check if instance is older than cutoff time
            if launch_time < cutoff_time:
                instance_name = 'N/A'
                created_at = 'N/A'
                
                # Extract instance name and creation time from tags
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                    elif tag['Key'] == 'CreatedAt':
                        created_at = tag['Value']
                
                old_instances.append({
                    'id': instance['InstanceId'],
                    'name': instance_name,
                    'launch_time': launch_time,
                    'age_hours': (datetime.now(timezone.utc) - launch_time).total_seconds() / 3600
                })
    
    return old_instances

def shutdown_instances(ec2_client, instance_ids):
    """Stop the specified instances."""
    if not instance_ids:
        return
    
    response = ec2_client.stop_instances(InstanceIds=instance_ids)
    return response

def main():
    # Configuration
    region = 'us-east-1'  # Change as needed
    max_age_hours = 24
    
    # Initialize EC2 client
    ec2 = boto3.client('ec2', region_name=region)
    
    print(f"Checking for instances older than {max_age_hours} hours in {region}...")
    
    # Get old instances
    old_instances = get_old_instances(ec2, hours=max_age_hours)
    
    if not old_instances:
        print("No instances found that need to be shut down.")
        return 0
    
    print(f"\nFound {len(old_instances)} instance(s) to shut down:")
    for instance in old_instances:
        print(f"  - {instance['name']} ({instance['id']}) - Age: {instance['age_hours']:.1f} hours")
    
    # Shutdown instances
    instance_ids = [inst['id'] for inst in old_instances]
    
    try:
        response = shutdown_instances(ec2, instance_ids)
        print(f"\nSuccessfully initiated shutdown for {len(instance_ids)} instance(s).")
        return 0
    except Exception as e:
        print(f"\nError shutting down instances: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
