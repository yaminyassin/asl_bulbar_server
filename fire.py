import threading
from firebase_admin import credentials, firestore, initialize_app
import scipy.io.wavfile as wav
import numpy as np

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
            
                doc.reference.update({
                    "processed": True,
                    "spectralData": {
                        "fbme": pathologyData["spectral_data"]["fbme"],
                        "sbme": pathologyData["spectral_data"]["sbme"],
                        "tbme": pathologyData["spectral_data"]["tbme"],
                    }
                }) 
           

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