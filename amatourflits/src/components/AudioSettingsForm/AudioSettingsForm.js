import React, { useState } from 'react';
import { FormControl, InputLabel, Typography, Select, MenuItem, Grid } from '@mui/material';
import styles from '../AudioForm/AudioForm.module.css';
import useAudioFiles from '../../hooks/useAudioFiles';

function AudioSettingsForm() {
  const [settings, setSettings] = useState({
    intro: '',
    outro: '',
    background: ''
  });

  const { audioFiles: introFiles } = useAudioFiles('amatourflits/intros');
  const { audioFiles: outroFiles } = useAudioFiles('amatourflits/outros');
  const { audioFiles: backgroundFiles } = useAudioFiles('amatourflits/bgaudio');

  const handleSettingChange = (setting, value) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      [setting]: value
    }));
  };

  return (
    <div className={styles.sentenceForm}>
      <Typography variant="h5" className={styles.typographyHeader}>
        Audio Settings
      </Typography>
      <Grid container spacing={2}>
        {/* Intro select */}
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel id="intro-label">Intro</InputLabel>
            <Select
              labelId="intro-label"
              value={settings.intro}
              onChange={(e) => handleSettingChange('intro', e.target.value)}
            >
              {introFiles.map((file, index) => (
                <MenuItem key={index} value={file.filename}>{file.filename}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        {/* Outro select */}
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel id="outro-label">Outro</InputLabel>
            <Select
              labelId="outro-label"
              value={settings.outro}
              onChange={(e) => handleSettingChange('outro', e.target.value)}
            >
              {outroFiles.map((file, index) => (
                <MenuItem key={index} value={file.filename}>{file.filename}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        {/* Background select */}
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel id="background-label">Achtergrond</InputLabel>
            <Select
              labelId="background-label"
              value={settings.background}
              onChange={(e) => handleSettingChange('background', e.target.value)}
            >
              {backgroundFiles.map((file, index) => (
                <MenuItem key={index} value={file.filename}>{file.filename}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </div>
  );
}

export default AudioSettingsForm;
