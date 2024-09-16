import base64
import datetime

import firebase_admin
from firebase_admin import storage
from rest_framework.response import Response

# Initialize Firebase Admin SDK
cred = firebase_admin.credentials.Certificate('media/serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'hamrokheti-5cbb1.appspot.com'
})

bucket = storage.bucket()


def upload_image(base64_image, folder_path, existing_image=None):
    # base64_image = request.data.get('product_image')
    if base64_image:
        try:
            image_data = base64.b64decode(base64_image.split(",")[1])
        except Exception as e:
            return Response({'status': 'FAILURE', 'message': 'Invalid base64 image data'})

        # Append timestamp to the image name
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        image_name = f'{folder_path}/image_{timestamp}.png'
        blob = bucket.blob(image_name)
        blob.upload_from_string(image_data, content_type='image/png')
        image_url = blob.generate_signed_url(expiration=datetime.timedelta(hours=2000))
        return image_url
    elif existing_image:
        # If no new image is provided, return the existing image URL
        return existing_image
    else:
        return None


