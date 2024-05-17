// navigator.mediaDevices.getUserMedia({ video: true })
//     .then(function (stream) {
//         var video = document.getElementById('video');
//         video.srcObject = stream;
//     })
//     .catch(function (err) {
//         console.log('Error accessing the camera:', err);
//     });

// document.getElementById('capture-btn').addEventListener('click', function () {
//     var video = document.getElementById('video');
//     var canvas = document.createElement('canvas');
//     var context = canvas.getContext('2d');
//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;
//     context.drawImage(video, 0, 0, canvas.width, canvas.height);
//     var dataURL = canvas.toDataURL('image/jpeg');

//     // form
//     var form = new FormData();
//     form.append('image', dataURL);

//     // send to server
//     fetch('/face_recognition', {
//         method: 'POST',
//         body: form
//     })
//         .then(response => {
//             if (response.ok) {
//                 console.log('Image sent successfully');
//                 window.location.href = '/dashboard'; // Redirect to dashboard if successful
//             } else {
//                 console.error('Failed to send image');
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//         });
// });
