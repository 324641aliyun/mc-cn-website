// 广告脚本
if (typeof adsEnabled !== 'undefined' && adsEnabled) {
    // 创建广告容器
    var adDiv = document.createElement('div');
    adDiv.style.cssText = 'position:fixed; bottom:20px; right:20px; width:300px; height:250px; background:rgba(255,255,255,0.8); backdrop-filter: blur(20px); border:1px solid rgba(255,255,255,0.6); border-radius:16px; box-shadow:0 8px 32px rgba(0,0,0,0.1); z-index:9999; display:flex; align-items:center; justify-content:center; font-size:14px; color:#1e293b;';
    adDiv.innerHTML = '广告位<br><span style="font-size:12px;color:#475569;">（此处可替换为 Google AdSense 代码）</span>';
    document.body.appendChild(adDiv);
}var adsEnabled = false;