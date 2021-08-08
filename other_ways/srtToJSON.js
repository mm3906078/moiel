var fs = require('fs');

fs.readFile('C:/Users/MohammdReza/Desktop/moiel/srt/The Shawshank Redemption 1994/English/The.Shawshank.Redemption.1994.1080p.BRRip.5.1.HEVC.x265-GIRAYS.srt', function(error, data) {  
    if(error)
        throw error;
        
    var text = data.toString();
    var lines = text.split('\n');

    var output = [];
    var buffer = {
        content: []
    };

    lines.forEach(function(line) {
        if(!buffer.id)
            buffer.id = line;
        else if(!buffer.start) {
            var range = line.split(' --> ');
            buffer.start = range[0];
            buffer.end = range[1];
        }
        else if(line !== '')
            buffer.content.push(line);
        else {
            output.push(buffer);
            buffer = {
                content: []
            };
        }
    });
    
    fs.writeFile('subtitle.json', JSON.stringify(output));
});