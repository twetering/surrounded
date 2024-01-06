import React from 'react';
import {useState} from 'react';
import PropTypes from 'prop-types'; // Import PropTypes
import { Button, Container, Paper, Typography, CircularProgress } from '@mui/material';
import styles from './AudioForm.module.css'; // import styles
import useVoices from '../../hooks/useVoices';
import useGenerateMultipleVoices from '../../hooks/useGenerateMultipleVoices';
import SentenceForm from '../SentenceForm/SentenceForm';
import useSentenceForm from '../../hooks/useSentenceForm';
import AudioSettingsForm from '../AudioSettingsForm/AudioSettingsForm';
import ReactPlayer from 'react-player';

function AudioForm() {
    const { voices } = useVoices();
    const { generateVoices, audioUrl, loading, error } = useGenerateMultipleVoices(); 
    const { sentences, addSentence, removeSentence, updateSentence } = useSentenceForm(voices);
    
    const [audiosettings, setAudioSettings] = useState({
        intro: '',
        outro: '',
        bgaudio: ''
    });

    const handleSettingChange = (setting, value) => {
        setAudioSettings(prevSettings => ({
            ...prevSettings,
            [setting]: value
        }));
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        generateVoices(sentences, audiosettings);
    };

    return (
        <Container className={styles.container}>
            <Paper className={styles.paper}>
                <Typography variant="h4" className={styles.typographyHeader}>
                    Meerdere Stemmen Genereren
                </Typography>

                <form onSubmit={handleSubmit}>
                    <AudioSettingsForm 
                        audiosettings={audiosettings} 
                        setAudioSettings={setAudioSettings} 
                    />

                    {sentences.map((sentence, index) => (
                        <SentenceForm
                            key={index}
                            index={index}
                            sentence={sentence}
                            voices={voices}
                            onSentenceChange={updateSentence}
                            onRemoveSentence={removeSentence}
                        />
                    ))}
                    <div className={styles.buttonGroup}>
                        <Button 
                            variant="contained" 
                            color="secondary" 
                            onClick={addSentence} 
                            className={styles.addRemoveButton}
                        >
                            Voeg Zin Toe
                        </Button>
                        <Button
                            type="submit"
                            variant="contained"
                            color="primary"
                            disabled={loading}
                            className={styles.submitButton}
                        >
                            {loading ? (
                                <>
                                    <CircularProgress 
                                        size={24} 
                                        className={styles.addRemoveButton} 
                                    />
                                    Genereren...
                                </>
                            ) : 'Genereer Stemmen'}
                        </Button>
                    </div>
                    {audioUrl && (
                        <div className={styles.audioSection}>
                            <Typography 
                                variant="h5" 
                                className={styles.typographyHeader}
                            >
                                Gegenereerde audio
                            </Typography>
                            <ReactPlayer
                                url={audioUrl}
                                controls={true}
                                className={styles.audioPlayer}
                            />
                        </div>
                    )}
                    {error && <div>Error: {error}</div>}
                </form>
            </Paper>
        </Container>
    );
}

AudioForm.propTypes = {
    sentences: PropTypes.arrayOf(PropTypes.shape({
        text: PropTypes.string,
        voiceId: PropTypes.string,
    })),
    voices: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string,
        voice_id: PropTypes.string,
    })),
};

export default AudioForm;
