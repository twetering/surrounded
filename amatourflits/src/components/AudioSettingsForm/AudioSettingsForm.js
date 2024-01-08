import React from 'react';
import { FormControl, InputLabel, Typography, Select, MenuItem, Grid } from '@mui/material';
import useAudioFiles from '../../hooks/useAudioFiles';

function AudioSettingsForm({ audiosettings, setAudioSettings }) {
    
    const { audioFiles: introFiles } = useAudioFiles('amatourflits/intros');
    const { audioFiles: outroFiles } = useAudioFiles('amatourflits/outros');
    const { audioFiles: bgaudioFiles } = useAudioFiles('amatourflits/bgaudio');

    const handleSettingChange = (setting, value) => {
        setAudioSettings(prevSettings => ({
            ...prevSettings,
            [setting]: value
        }));
    };
    

  return (
    <div className="AudioSettingsForm">
      <box className="typographyHeader">
      <Typography variant="h5" className="typographyHeader">
        Algemeen ontwerp
      </Typography>
      </box>
      <Grid container spacing={2}>
        
        {/* Intro select */}
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel id="intro-label">Intro (start van je audiobestand)</InputLabel>
            <Select
              labelId="intro-label"
              value={audiosettings.intro}
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
            <InputLabel id="outro-label">Outro (einde van je audiobestand)</InputLabel>
            <Select
              labelId="outro-label"
              value={audiosettings.outro}
              onChange={(e) => handleSettingChange('outro', e.target.value)}
              >
              {outroFiles.map((file, index) => (
                <MenuItem key={index} value={file.filename}>{file.filename}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        {/* BGaudio select */}
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel id="bgaudio-label">Achtergrond (audio op de achtergrond)</InputLabel>
            <Select
              labelId="bgaudio-label"
              value={audiosettings.bgaudio}
              onChange={(e) => handleSettingChange('bgaudio', e.target.value)}
              >
              {bgaudioFiles.map((file, index) => (
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
