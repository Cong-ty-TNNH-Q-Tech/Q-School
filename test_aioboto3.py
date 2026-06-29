import asyncio
import aioboto3

async def test():
    session = aioboto3.Session()
    async with session.client('s3', aws_access_key_id='test', aws_secret_access_key='test', endpoint_url='http://localhost:9000') as client:
        try:
            url = await client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': 'test', 'Key': 'test'},
                ExpiresIn=3600
            )
            print("IS ASYNC:", url)
        except TypeError as e:
            if "object string can't be used in 'await' expression" in str(e):
                url = client.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={'Bucket': 'test', 'Key': 'test'},
                    ExpiresIn=3600
                )
                print("IS SYNC:", url)
            else:
                print("ERROR:", e)

asyncio.run(test())
