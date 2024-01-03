// src/components/SentenceForm/SentenceForm.js
import React from 'react';
import { TextField, FormControl, Typography, InputLabel, Select, MenuItem, Button } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import styles from '../AudioForm/AudioForm.module.css';
import useAudioFiles from '../../hooks/useAudioFiles';

const SentenceForm = ({ index, sentence, voices, onSentenceChange, onRemoveSentence }) => {
    const { audioFiles: bgVoices, loading: loadingBgVoices } = useAudioFiles('amatourflits/bgvoice');

    const bgVoiceFolder = 'amatourflits/bgvoice/';

    const bgVoiceId = sentence.bgVoiceId || '';

    const handleBgVoiceChange = (index, filename) => {
        const fullPath = bgVoiceFolder + filename;
        onSentenceChange(index, 'bgVoiceId', fullPath);
    };
    
    return (
        <div className={styles.audioForm}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
                <TextField
                    label={`Zin ${index + 1}`}
                    multiline
                    rows={2}
                    style={{ marginRight: '10px', flexGrow: 1 }}
                    variant="outlined"
                    value={sentence.text}
                    onChange={(e) => onSentenceChange(index, 'text', e.target.value)}
                />
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <FormControl style={{ width: '200px', marginRight: '10px' }}>
                        <InputLabel id={`voice-select-label-${index}`}>Stem</InputLabel>
                        <Select
                            labelId={`voice-select-label-${index}`}
                            id={`voice-select-${index}`}
                            value={sentence.voiceId}
                            label="Stem"
                            onChange={(e) => onSentenceChange(index, 'voiceId', e.target.value)}
                        >
                            {voices.map((voice) => (
                                <MenuItem key={voice.voice_id} value={voice.voice_id}>
                                    {voice.name}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>

                    {/* BgVoice Select */}
                    <FormControl style={{ width: '200px', marginRight: '10px' }}>
                        <InputLabel id={`bgvoice-select-label-${index}`}>Achtergrond</InputLabel>
                        <Select
                            labelId={`bgvoice-select-label-${index}`}
                            id={`bgvoice-select-${index}`}
                            value={bgVoiceId ? bgVoiceId.replace(bgVoiceFolder, '') : ''} // Alleen de bestandsnaam
                            label="Achtergrond"
                            onChange={(e) => handleBgVoiceChange(index, e.target.value)}
                        >
                            {bgVoices.map((bgVoice, idx) => (
                                <MenuItem key={idx} value={bgVoice.filename}>{bgVoice.filename}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>

                    <Button variant="outlined" color="secondary" onClick={() => onRemoveSentence(index)}>
                        <DeleteIcon />
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default SentenceForm;
