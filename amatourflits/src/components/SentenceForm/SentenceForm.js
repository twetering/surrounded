// src/components/SentenceForm/SentenceForm.js
import React from 'react';
import { Box, TextField, IconButton, InputAdornment, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
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
        <div className="sentenceForm">
            <div className="flexContainer">
                <Box mb={2} className="textField">
                    <TextField
                        label={`Fragment ${index + 1}`}
                        multiline
                        rows={5}
                        fullWidth
                        variant="outlined"
                        value={sentence.text}
                        onChange={(e) => onSentenceChange(index, 'text', e.target.value)}
                        InputProps={{
                            endAdornment: (
                                <InputAdornment position="end">
                                    <IconButton onClick={() => onRemoveSentence(index)}>
                                        <DeleteIcon />
                                    </IconButton>
                                </InputAdornment>
                            ),
                        }}
                    />
                </Box>
                <div className="flexItem">
                    <div className="formControls">
                        {/* Voice Select */}
                        <Box mb={2} className="formControl">
                            <FormControl fullWidth>
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
                        </Box>
                        {/* BgVoice Select */}
                        <Box mb={2} className="formControl">
                            <FormControl fullWidth>
                                <InputLabel id={`bgvoice-select-label-${index}`}>Achtergrond</InputLabel>
                                <Select
                                    labelId={`bgvoice-select-label-${index}`}
                                    id={`bgvoice-select-${index}`}
                                    value={bgVoiceId ? bgVoiceId.replace(bgVoiceFolder, '') : ''} // Only show filename
                                    label="Achtergrond"
                                    onChange={(e) => handleBgVoiceChange(index, e.target.value)}
                                    disabled={loadingBgVoices} // Disable select while loading
                                >
                                {loadingBgVoices ? (
                                    <MenuItem value="">
                                        <em>Loading...</em>
                                    </MenuItem>
                                ) : (
                                bgVoices.map((bgVoice, idx) => (
                                    <MenuItem key={idx} value={bgVoice.filename}>{bgVoice.filename}</MenuItem>
                                    ))
                                )}
                                </Select>
                            </FormControl>
                        </Box>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SentenceForm;
