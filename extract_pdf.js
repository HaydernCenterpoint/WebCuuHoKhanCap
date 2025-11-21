const fs = require('fs');
const pdf = require('pdf-parse');

const pdfPath = 'c:\\Users\\ADMIN\\Desktop\\Tét2222\\mở quyền sửa đổi - HOÀN THIỆN - KV.pdf';

const dataBuffer = fs.readFileSync(pdfPath);

pdf(dataBuffer).then(function (data) {
    fs.writeFileSync('pdf_content.txt', data.text, 'utf8');
    console.log('Done');
}).catch(function (error) {
    console.error('Error:', error);
});
