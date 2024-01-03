// src/components/SentenceForm/SentenceForm.js
import React from 'react';
import { TextField, FormControl, InputLabel, Select, MenuItem, Button } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

const SentenceForm = ({ index, sentence, voices, onSentenceChange, onRemoveSentence }) => {
    return (
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
                <Button variant="outlined" color="secondary" onClick={() => onRemoveSentence(index)}>
                    <DeleteIcon />
                </Button>
            </div>
        </div>
    );
};

export default SentenceForm;
