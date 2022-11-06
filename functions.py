import numpy as np
import numpy.typing as npt
from scipy.fft import fft, fftfreq



def getBandPoints(frequencies, magnitudes):
    fbme_x = 0
    fbme_y = 0

    sbme_x = 0
    sbme_y = 0

    tbme_x = 0
    tbme_y = 0

    for i in range(len(frequencies)):

        currentFrequency = frequencies[i]
        currentMagnitude = magnitudes[i]
        
        if currentFrequency >= 0 and currentFrequency <= 420:
            if currentMagnitude > fbme_y:
                fbme_x = currentFrequency
                fbme_y = currentMagnitude
            
        elif currentFrequency >= 421 and currentFrequency <= 1260:
            if currentMagnitude > sbme_y:
                sbme_x = currentFrequency
                sbme_y = currentMagnitude

        elif currentFrequency >= 2100 and currentFrequency <= 5880:
            if currentMagnitude > tbme_y:
                tbme_x = currentFrequency
                tbme_y = currentMagnitude
    
    return {"fbme": {"x": fbme_x, "y": fbme_y}, 
        "sbme": {"x": sbme_x, "y": sbme_y}, 
        "tbme": {"x": tbme_x, "y": tbme_y}}


def getSpectralData(signal: npt.ArrayLike , frameSize: int, stepSize: int, sampleRate: int,  ):

    signal_frames = [] 
    signal_fft = [] #
    signal_fft_frequencies = [] 
    signal_fft_magnitudes = [] 
    
    spectral_data = {
        "fbme": [],
        "sbme": [],
        "tbme": [],
        "lbst": [],
        "hbst": [],
    }

    n_points = 4096
    step = 0

    while signal.size - step >= stepSize:
        
        frame = signal[step: step + frameSize]
        fft_frame = fft(frame, n= n_points)
        fft_frequencies =np.abs(fftfreq(n= n_points, d= 1/sampleRate))
        fft_magnitudes = 10* np.log10(np.abs(fft_frame))

        signal_frames.append(frame)
        signal_fft.append(fft)
        signal_fft_frequencies.append(fft_frequencies)
        signal_fft_magnitudes.append(fft_magnitudes)

        spectralPoints = getBandPoints(fft_frequencies, fft_magnitudes)

        lbst = (spectralPoints["sbme"]["y"] - spectralPoints["fbme"]["y"]) / ( spectralPoints["sbme"]["x"] - spectralPoints["fbme"]["x"])
        hbst = (spectralPoints["tbme"]["y"] - spectralPoints["sbme"]["y"]) / ( spectralPoints["tbme"]["x"] - spectralPoints["sbme"]["x"])

        spectral_data["fbme"].append(spectralPoints.get("fbme"))
        spectral_data["sbme"].append(spectralPoints.get("sbme"))
        spectral_data["tbme"].append(spectralPoints.get("tbme"))
        spectral_data["lbst"].append(lbst)
        spectral_data["hbst"].append(hbst)
        
        step += stepSize

    return {
        "frames": signal_frames,
        "fft": signal_fft,
        "fft_frequencies": signal_fft_frequencies, 
        "fft_magnitudes": signal_fft_magnitudes, 
        "spectral_data": spectral_data
        }




