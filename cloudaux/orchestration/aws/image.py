from cloudaux.aws.ec2 import describe_images
from cloudaux.aws.ec2 import describe_image_attribute
from cloudaux.decorators import modify_output
from flagpole import FlagRegistry, Flags

registry = FlagRegistry()
FLAGS = Flags('BASE', 'KERNEL', 'RAMDISK', 'LAUNCHPERMISSION', 'PRODUCTCODES')


@registry.register(flag=FLAGS.KERNEL)
def get_kernel(image, **conn):
    attribute = describe_image_attribute(
        Attribute='kernel', ImageId=image['ImageId'], **conn)
    return dict(KernelId=attribute['KernelId'])


@registry.register(flag=FLAGS.RAMDISK)
def get_ramdisk(image, **conn):
    attribute = describe_image_attribute(
        Attribute='ramdisk', ImageId=image['ImageId'], **conn)
    return dict(RamdiskId=attribute['RamdiskId'])


@registry.register(flag=FLAGS.LAUNCHPERMISSION)
def get_launch_permission(image, **conn):
    attribute = describe_image_attribute(
        Attribute='launchPermission', ImageId=image['ImageId'], **conn)
    return dict(LaunchPermissions=attribute['LaunchPermissions'])


@registry.register(flag=FLAGS.PRODUCTCODES)
def get_product_codes(image, **conn):
    attribute = describe_image_attribute(
        Attribute='productCodes', ImageId=image['ImageId'], **conn)
    return dict(ProductCodes=attribute['ProductCodes'])


@registry.register(flag=FLAGS.BASE)
def get_base(image, **conn):
    image = describe_images(ImageIds=[image['ImageId']], **conn)
    image = image[0]
    arn = 'arn:aws:ec2:{region}::image/{imageid}'.format(
        region=conn['region'],
        imageid=image['ImageId'])
    image.update({'Arn': arn, 'Region': conn['region'], '_version': 1})
    return image


@modify_output
def get_image(image_id, flags=FLAGS.ALL, **conn):
    """
    Orchestrates all the calls required to fully build out an EC2 Image (AMI, AKI, ARI)

    {
        "Architecture": "x86_64", 
        "Arn": "arn:aws:ec2:us-east-1::image/ami-11111111", 
        "BlockDeviceMappings": [], 
        "CreationDate": "2013-07-11T16:04:06.000Z", 
        "Description": "...", 
        "Hypervisor": "xen", 
        "ImageId": "ami-11111111", 
        "ImageLocation": "111111111111/...", 
        "ImageType": "machine", 
        "KernelId": "aki-88888888", 
        "LaunchPermissions": [], 
        "Name": "...", 
        "OwnerId": "111111111111", 
        "ProductCodes": [], 
        "Public": false, 
        "RamdiskId": {}, 
        "RootDeviceName": "/dev/sda1", 
        "RootDeviceType": "ebs", 
        "SriovNetSupport": "simple",
        "State": "available", 
        "Tags": [], 
        "VirtualizationType": "hvm", 
        "_version": 1
    }

    :param image_id: str ami id
    :param flags: By default, set to ALL fields
    :param conn: dict containing enough information to make a connection to the desired account.
    Must at least have 'assume_role' key.
    :return: dict containing a fully built out image.
    """
    image = dict(ImageId=image_id)
    conn['region'] = conn.get('region', 'us-east-1')
    return registry.build_out(flags, image, **conn)
