document.addEventListener('DOMContentLoaded', () => {
    const descriptions = {
        "danceability": "0% = least danceable and 100% = most danceable based on tempo, rhythm stability, and overall regularity.",
        "energy": "0% = low energy and 100% = high energy based on dynamic range, perceived loudness, timbre, onset rate, and general entropy. Typically, energetic tracks feel fast, loud, and noisy.",
        "speechiness": "TLDR: 0% = less speech & 100% = more speech \n \n The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 100% the attribute value. Values above 66% describe tracks that are probably made entirely of spoken words. Values between 33% and 66% describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 33% most likely represent music and other non-speech-like tracks.",
        "acousticness": "A confidence measure from 0% to 100% of whether the track is acoustic.",
        "instrumentalness": "TLDR: 0% = more instrumental, less vocals & 100% = less instrumental, more vocals. \n \n Predicts whether a track contains no vocals. 'Ooh' and 'aah' sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly 'vocal'. The closer the instrumentalness value is to 100%, the greater likelihood the track contains no vocal content. Values above 50% are intended to represent instrumental tracks, but confidence is higher as the value approaches 100%",
        "valence": "A measure from 0% to 100% describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).",
        "key": "The key in which the track is composed.",
        "time_signature": "An estimated time signature. The time signature (meter) is a notational convention to specify how many beats are in each bar (or measure). The time signature ranges from 3 to 7 indicating time signatures of 3/4, to 7/4.",
        "mode": "The modality (major or minor) of the track. Yellow indicates a major key whereas Purple indicates a minor key.",
        "loudness": "The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typically range between -60 and 0 db. A db value closer to 0 in this case indicates more loudness.",
        "tempo": "The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration."
    };

    document.querySelectorAll('select').forEach(select => {
        select.addEventListener('mouseover', event => {
            if (event.target.tagName.toLowerCase() === 'option') {
                const description = descriptions[event.target.value];
                if (description) {
                    const tooltip = document.createElement('div');
                    tooltip.className = 'tooltiptext';
                    tooltip.innerHTML = description.replace(/\n/g, '<br>'); // Replace new lines with <br>
        
                    // Adjust width based on text length
                    if (description.length > 150) {
                        tooltip.style.width = '400px';
                    } else {
                        tooltip.style.width = '200px';
                    }

                    event.target.closest('.tooltip').appendChild(tooltip);
                }
            }
        });

        select.addEventListener('mouseout', event => {
            if (event.target.tagName.toLowerCase() === 'option') {
                const tooltip = event.target.closest('.tooltip').querySelector('.tooltiptext');
                if (tooltip) {
                    tooltip.remove();
                }
            }
        });
    });
});
