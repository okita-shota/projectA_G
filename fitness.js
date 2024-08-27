const video = document.getElementById('video');
const countElement = document.getElementById('count');
let count = 0;

// カメラへのアクセス許可を取得
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    // ビデオ要素にストリームを設定
    video.srcObject = stream;
  })
  .catch(err => {
    console.error('カメラへのアクセスに失敗しました', err);
  });

// カウントアップボタンのイベントリスナー
const countButton = document.getElementById('countButton');
countButton.addEventListener('click', () => {
  count++;
  countElement.textContent = count;
});

// ビデオ要素のロード完了時のイベントリスナー
video.addEventListener('loadedmetadata', () => {
  // ビデオの幅と高さを設定
  video.width = video.videoWidth;
  video.height = video.videoHeight;
});

// ビデオ再生時のイベントリスナー
video.addEventListener('play', () => {
  // 定期的にフレームをキャプチャ
  setInterval(() => {
    // フレームをキャプチャ
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // フレームを画像データに変換
    const imageData = canvas.toDataURL('image/jpeg');

    // 画像認識処理など
    // ここでは、画像データを用いてカウントアップ処理を行う
    // 例: 画像認識で特定の動作が検出された場合にカウントアップ

  }, 1000); // 1秒ごとにフレームをキャプチャ
});

// 終了ボタンのイベントリスナー
const stopButton = document.getElementById('stopButton');
stopButton.addEventListener('click', () => {
  // ビデオストリームを停止
  const stream = video.srcObject;
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    video.srcObject = null;
  }
});
