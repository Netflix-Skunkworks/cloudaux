# CloudAux AWS Image

CloudAux can build out a JSON object describing an EC2 Image.

## Example

    from cloudaux.orchestration.aws.image import get_image, FLAGS
    from cloudaux.aws.ec2 import describe_images

    conn = {
        'account_number': '111111111111',
        'assume_role': 'MyRole',
        'session_name': 'MySession',
        'region': 'us-east-1'
    }

    # List images in Region
    # NOTE: Filter by owner-id or this will take forever to return.
    images = describe_images(**conn)

    # List images in region owned by 111111111111
    images = describe_images(Owners=['111111111111'])

    # List public images in region owned by 111111111111
    describe_images(Filters=[{'Name': 'is-public', 'Values': ['true']}, {'Name': 'owner-id', 'Values': ['111111111111']}])

    # By Image ID
    image = get_image('ami-11111111', flags=FLAGS.ALL, **conn)

    all_images = list()
    for image im all_images:
        all_images.append(get_image(image['ImageId'], **conn))


## Flags

The `get_image` command accepts flags describing what parts of the structure to build out.

    from cloudaux.orchestration.aws.image import FLAGS

    desired_flags = FLAGS.BASE | FLAGS.LAUNCHPERMISSION
    image = get_image('ami-11111', flags=desired_flags, **conn)

If not provided, `get_image` assumes `FLAGS.ALL`.

- [BASE](#flagsbase)
- [KERNEL](#flagskernel)
- [RAMDISK](#flagsramdisk)
- [LAUNCHPERMISSION](#flagslaunchpermission)
- [PRODUCTCODES](#flagsproductcodes)

### FLAGS.BASE

Call boto3's [`client.describe_images`](http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_images).

    {
      "Architecture": "x86_64", 
      "Arn": "arn:aws:ec2:us-east-1::image/ami-11111111", 
      "BlockDeviceMappings": [
        {
          "DeviceName": "/dev/sda1", 
          "Ebs": {
            "DeleteOnTermination": true, 
            "Encrypted": false, 
            "SnapshotId": "snap-11111111", 
            "VolumeSize": 8, 
            "VolumeType": "standard"
          }
        }, 
        {
          "DeviceName": "/dev/sdb", 
          "VirtualName": "ephemeral0"
        }
      ], 
      "CreationDate": "2013-07-11T16:04:06.000Z", 
      "Description": "...", 
      "Hypervisor": "xen", 
      "ImageId": "ami-11111111", 
      "ImageLocation": "111111111111/...", 
      "ImageType": "machine", 
      "KernelId": "aki-11111111", 
      "Name": "...", 
      "OwnerId": "111111111111", 
      "Public": false, 
      "RootDeviceName": "/dev/sda1", 
      "RootDeviceType": "ebs", 
      "State": "available", 
      "Tags": [], 
      "VirtualizationType": "paravirtual", 
      "_version": 1
    }


## FLAGS.KERNEL

    {
      "KernelId": {
        "Value": "aki-11111111"
      }
    }


## FLAGS.RAMDISK

    {
      "RamdiskId": {}
    }


## FLAGS.LAUNCHPERMISSION

    {
      "LaunchPermissions": [
        {
          "UserId": "111111111111"
        }, 
        {
          "UserId": "222222222222"
        }
      ]
    }


## FLAGS.PRODUCTCODES

    {
      "ProductCodes": []
    }