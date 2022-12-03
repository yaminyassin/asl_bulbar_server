import threading
from firebase_admin import credentials, firestore, initialize_app
import scipy.io.wavfile as wav
from functions import getSpectralData

class StoreListener(threading.Thread):

    def __init__(self):
        super().__init__()
        cred = credentials.Certificate(".env_files/serviceAccountKey.json")
        initialize_app(cred)
        self.db = firestore.client()
        self._callback = threading.Event()
        print("StoreListener initialized")

    def stop(self):
        self._callback.set()

    def stopped(self):
        return self._callback.is_set()

    def on_snapshot(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Found document: {doc.id}")

            if doc.reference.get().to_dict().get("processed") == False:
                print("Processing")
                audioData = doc.reference.get().to_dict().get("audioFile")
                print('AUDIO DATA: ', audioData)
                pathologySampleRate, pathologySignal = wav.read("./ALS/Pathology/008.wav")
                frameSize = 1323
                stepSize = 441
                pathologyData = getSpectralData(signal=pathologySignal, frameSize=frameSize, stepSize=stepSize, sampleRate=pathologySampleRate)
                # print patholgyData types
                print("Pathology Data Types: ", type(pathologyData))
                print("Pathology Data Keys: ", pathologyData.keys())
                print("Pathology Data Frames: ", type(pathologyData.get("frames")))
                print("Pathology Data FFT: ", type(pathologyData.get("fft")))
                print("Pathology Data FFT Frequencies: ", type(pathologyData.get("fft_frequencies")))
                print("Pathology Data FFT Magnitudes: ", type(pathologyData.get("fft_magnitudes")))
                print("Pathology Data Spectral Data: ", type(pathologyData.get("spectral_data")))
                print("Pathology Data Spectral Data Keys: ", pathologyData.get("spectral_data").keys())
                print("Pathology Data Spectral Data FBME: ", type(pathologyData.get("spectral_data").get("fbme")))
                print("Pathology Data Spectral Data SBME: ", type(pathologyData.get("spectral_data").get("sbme")))
                print("Pathology Data Spectral Data TBME: ", type(pathologyData.get("spectral_data").get("tbme")))
                print("Pathology Data Spectral Data LBST: ", type(pathologyData.get("spectral_data").get("lbst")))
                print("Pathology Data Spectral Data LBST Keys: ", pathologyData.get("spectral_data").get("lbst"))


                #write to document
                """
                doc.reference.update({
                    "processed": True,
                    "audioData": {
                        "fft": pathologyData.get("fft"),
                        "fft_frequencies": pathologyData.get("fft_frequencies"),
                        "fft_magnitudes": pathologyData.get("fft_magnitudes"),
                        "frames": pathologyData.get("frames"),
                        "spectral_data": pathologyData.get("spectral_data"),
                        "sampleRate": pathologySampleRate,
                        "frameSize": frameSize,
                        "stepSize": stepSize,
                    },
                })
                """

                print("Done processing")
                self.stop()


    def run(self):
        while not self.stopped():
            print("Listening for changes", self.stopped())
            collectionQuery = self.db.collection("audioData").where(u'processed', u'==', False)
            collectionQuery.on_snapshot(self.on_snapshot)
            self._callback.wait(30)





if __name__ == "__main__":
    storeListener = StoreListener()
    storeListener.run()