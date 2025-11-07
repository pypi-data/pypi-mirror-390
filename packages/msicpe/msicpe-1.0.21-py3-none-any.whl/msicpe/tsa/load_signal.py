import numpy as np
import os

def _impulse_noise(sig,ratio):
    # Generating noise
    # Generate a noise sample consisting of values that are a little higer or lower than a few randomly selected values in the original data. 
    noise_sample = np.random.default_rng().uniform(0.75*max(sig), max(sig), int(ratio*len(sig)))
    # Generate an array of zeros with a size that is the difference of the sizes of the original data an the noise sample.
    zeros = np.zeros(len(sig) - len(noise_sample))
    # Add the noise sample to the zeros array to obtain the final noise with the same shape as that of the original data.
    noise = np.concatenate([noise_sample, zeros])
    # Shuffle the values in the noise to make sure the values are randomly placed.
    np.random.shuffle(noise)
    # Obtain data with the noise added.
    return noise

def load_signal(dataName,dataKey=None,addImpulseNoise=False):
    """
    load_signal charge le signal échantillonné et sa fréquence d'échantillonnage d'un fichier fourni.
    
    Puis, il est transformé comme suit :
    
    sig = int8(128*(sig-np.mean(sig)))
    
    Enfin, il est sous-échantilloné pour réduire le nombre de points

    Parameters
    ----------
    dataName : string
        nom du fichier contenant le signal. Doit être 'Sensor','EEG','ENR' ou 'audio'
                
    dataKey : string, optional
        clé du signal à extraire du fichier (car les fichiers 'Sensor' et 'ENR' contiennent plusieurs clés)
        Sensor : chosir parmi 'Temperature_Celsius(℃)','Relative_Humidity(%)','Abs Humidity(g/m³)','DPT(℃)' ou 'VPD(kPa)'
        ENR : choisir parmi 'Vitesse du vent à 100m (m/s)' ou 'Rayonnement solaire global (W/m2)'
    
    addImpulseNoise : bool, optional
        Si True, du bruit impulsionnel est ajouté au signal.
        Le défaut est False.
        
    Returns
    -------
    Fs : float64
        fréquence d'échantillonagé du signal 
    
    sig : ndarray
        signal lu dans le fichier
    """
    Fs=None
    sig=None
    if "audio" in dataName.lower():
        from scipy.io import wavfile
        fileName=os.path.join(os.path.dirname(__file__), 'data/ProtestMonoBruitTronque.wav')
        Fs, sig = wavfile.read(fileName)
        sig = 255 * sig
        Fs = Fs
        Fs = Fs/2
        sig=sig[::2].flatten()
        sig=sig.flatten()
    elif "eeg" in dataName.lower():
        import pandas as pd
        fileName=os.path.join(os.path.dirname(__file__), 'data/EEG.csv')
        dataKey="EEG"
        data=pd.read_csv(fileName)
        Fs=1/np.mean(data['Time'].values[1:]-data['Time'].values[:-1]).astype(float)
        sig=data[dataKey].values
        if addImpulseNoise:
            sig = sig*64 + _impulse_noise(sig,0.001)
        else:
            sig = sig*64

    elif "sensor" in dataName.lower():
        import re
        import pandas as pd
        fileName=os.path.join(os.path.dirname(__file__), 'data/Sensor_data.csv')
        with open(fileName, "r") as f:
            content=f.readlines()
            pattern = '"\d+,\d+"'
            for c in range(len(content)):
                result = re.findall(pattern, content[c])
                new = [i.replace('"','').replace(',','.') for i in result]
                for i in range(len(result)):
                    content[c]=content[c].replace(result[i],new[i])
        with open(fileName, "w") as f:
            f.write(''.join(content))
        data=pd.read_csv(fileName)
        data['Timestamp']=data['Timestamp'].values.astype('datetime64[s]')
        data['Timestamp']=data['Timestamp'].values-data['Timestamp'].values[0]
        Fs= 1/np.mean(data['Timestamp'].values[1:]-data['Timestamp'].values[:-1]).astype(float)
        if dataKey is not None:#=="Abs Humidity(g/m³)":
            try:
                sig=data[dataKey].values-np.mean(data[dataKey].values)
                sig = sig*128/(max(sig))
                sig = sig[::12]
                Fs = Fs/12
                if addImpulseNoise:
                    sig = sig + _impulse_noise(sig,0.01)
            except KeyError:
                raise KeyError('Please select a dataKey from the following ones : '+', '.join(data.columns[1:]))
        else:
            raise ValueError('Please select a dataKey from the following ones : '+', '.join(data.columns[1:]))
    elif 'enr' in dataName.lower():
        import pandas as pd
        fileName=os.path.join(os.path.dirname(__file__), 'data/ENR.csv')
        with open(fileName, "r") as f:
            content=f.readlines()
            for c in range(len(content)):
                content[c]=content[c].replace('+02:00','').replace('+01:00','')
        with open(fileName, "w") as f:
            f.write(''.join(content))
        data=pd.read_csv(fileName,delimiter=";")
        data['Date']=data['Date'].values.astype('datetime64[s]')
        data['Date']=data['Date'].values-data['Date'].values[0]
        Fs=1/np.mean(data['Date'].values[1:]-data['Date'].values[:-1]).astype(float)
        # if dataKey=='Vitesse du vent à 100m (m/s)':
        try:
            if dataKey=='Vitesse du vent à 100m (m/s)':
                sig=data[dataKey].values-np.mean(data[dataKey].values)
                sig = sig*128/(max(sig))
                sig = sig[2::16]
                Fs = Fs/16
            elif dataKey=='Rayonnement solaire global (W/m2)':
                sig=data[dataKey].values-np.mean(data[dataKey].values)
                sig = sig*128/(max(sig))
                sig = sig[2::16]
                Fs = Fs/16
            if addImpulseNoise:
                sig = sig + _impulse_noise(sig,0.01)
        except KeyError:
            raise KeyError('Please select a dataKey from the following ones : '+', '.join(data.columns[1:]))
        # else:
        #     raise KeyError('Please select the dataKey "Vitesse du vent à 100m (m/s)"')
    sig = sig.astype(np.int8)
    sig = sig.flatten()
    return Fs, sig
