// Suraksha Setu v4 — QR photo scan (BarcodeDetector, Chrome/Android).
// Sirf status return karta hai — UI messages app.js/i18n ke paas hain.
export async function scanQRFile(f){
  if(!f) return { status: 'empty' };
  if(!('BarcodeDetector' in window)) return { status: 'unsupported' };
  try{
    const bmp = await createImageBitmap(f);
    const det = new BarcodeDetector({ formats: ['qr_code'] });
    const codes = await det.detect(bmp);
    if(codes.length) return { status: 'ok', value: codes[0].rawValue };
    return { status: 'notfound' };
  }catch(e){
    return { status: 'error' };
  }
}
