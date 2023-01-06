import settings
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS,cross_origin
from views import router
from middleware import model_predict

app = Flask(__name__)
socketio = SocketIO(app)
app.config["UPLOAD_FOLDER"] = settings.UPLOAD_FOLDER
app.secret_key = "secret key"
app.register_blueprint(router)
# socketio = SocketIO(app)
# socketio.init_app(app, cors_allowed_origins="*")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=settings.API_DEBUG_FLAG)


@socketio.on('image')
def image(data_image):
    #print(data_image)
    # frame = (readb64(data_image))
    # imgencode = cv2.imencode('.jpeg', frame,[cv2.IMWRITE_JPEG_QUALITY,40])[1]

    # # base64 encode
    # stringData = base64.b64encode(imgencode).decode('utf-8')
    # b64_src = 'data:image/jpeg;base64,'
    # stringData = b64_src + stringData

    out_data = model_predict(data_image, is_streaming=True, annotation_style='bbox', show_heuristic=False)

    # emit the frame back
    print('FPS')
    print(out_data[-25:])
    emit('response_back', out_data)