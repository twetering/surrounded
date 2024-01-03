import { useState, useEffect } from 'react';

const useAudioFiles = (folder) => {
    const [audioFiles, setAudioFiles] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch(`http://127.0.0.1:5000/api/audio?folder=${folder}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => setAudioFiles(data.files))
            .catch(error => console.error('Error loading audio files:', error))
            .finally(() => setLoading(false));
    }, [folder]);

    return { audioFiles, loading };
};

export default useAudioFiles;