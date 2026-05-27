import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# 🔑 從 Vercel 環境變數讀取 OIDC 帳密
CLIENT_ID = os.environ.get('TDX_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('TDX_CLIENT_SECRET', '')

# 🎨 完美還原 Figma 設計稿的單一 HTML + Tailwind CSS 範本
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>列車時刻查詢</title>
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="bg-gray-100 p-6 min-h-screen flex flex-col items-center justify-start gap-6">

  <form action="/" method="POST" class="w-full max-w-md bg-[#3A3A3A] text-white p-4 rounded-lg shadow-lg font-sans">
    
    <div class="bg-[#1D4ED8] px-4 py-2 rounded-t-md flex justify-between items-center mb-4">
      <span class="text-sm font-bold">列車時刻查詢 (正式版)</span>
      <span class="text-xs">▼</span>
    </div>

    <div class="mb-4 flex items-center gap-3">
      <div class="flex-1 space-y-2">
        <div>
          <label class="block text-xs text-gray-300 mb-1">出發站</label>
          <select name="start_station" id="start_station" class="w-full bg-white text-gray-800 px-3 py-2 rounded border border-gray-400 text-sm">
            <option value="1000" {% if form_data.start_station == '1000' %}selected{% endif %}>1000-臺北</option>
            <option value="1060" {% if form_data.start_station == '1060' %}selected{% endif %}>1060-桃園</option>
            <option value="3300" {% if form_data.start_station == '3300' %}selected{% endif %}>3300-臺中</option>
            <option value="4220" {% if form_data.start_station == '4220' %}selected{% endif %}>4220-台南</option>
            <option value="4400" {% if form_data.start_station == '4400' %}selected{% endif %}>4400-高雄</option>
            <option value="7000" {% if form_data.start_station == '7000' %}selected{% endif %}>7000-花蓮</option>
          </select>
        </div>
        <div>
          <label class="block text-xs text-gray-300 mb-1">抵達站</label>
          <select name="end_station" id="end_station" class="w-full bg-white text-gray-800 px-3 py-2 rounded border border-gray-400 text-sm">
            <option value="1000" {% if form_data.end_station == '1000' %}selected{% endif %}>1000-臺北</option>
            <option value="1060" {% if form_data.end_station == '1060' %}selected{% endif %}>1060-桃園</option>
            <option value="3300" {% if form_data.end_station == '3300' %}selected{% endif %}>3300-臺中</option>
            <option value="4220" {% if form_data.end_station == '4220' %}selected{% endif %}>4220-台南</option>
            <option value="4400" {% if form_data.end_station == '4400' %}selected{% endif %}>4400-高雄</option>
            <option value="7000" {% if form_data.end_station == '7000' %}selected{% endif %}>7000-花蓮</option>
          </select>
        </div>
      </div>
      
      <button type="button" onclick="swapStations()" class="bg-[#4B5563] p-2 rounded hover:bg-gray-500 self-end mb-1 cursor-pointer">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"/></svg>
      </button>
    </div>

    <div class="mb-4 space-y-3">
      <input type="hidden" name="time_type" id="time_type" value="{{ form_data.time_type }}">
      <div class="flex w-full rounded overflow-hidden text-sm border border-[#1D4ED8]">
        <button type="button" id="btn_dept" onclick="toggleTimeType('departure')" class="flex-1 py-1.5 text-center font-medium cursor-pointer {% if form_data.time_type == 'departure' %}bg-[#1D4ED8]{% else %}bg-[#4B5563] text-gray-300{% endif %}">出發時間</button>
        <button type="button" id="btn_arr" onclick="toggleTimeType('arrival')" class="flex-1 py-1.5 text-center font-medium cursor-pointer {% if form_data.time_type == 'arrival' %}bg-[#1D4ED8]{% else %}bg-[#4B5563] text-gray-300{% endif %}">抵達時間</button>
      </div>

      <div>
        <input type="date" name="search_date" value="{{ form_data.search_date }}" class="w-full bg-white text-gray-800 px-3 py-2 rounded text-sm">
      </div>

      <div class="flex items-center gap-2">
        <input type="text" value="00:00" readonly class="w-full bg-gray-200 text-gray-500 px-3 py-2 rounded text-sm text-center select-none">
        <span class="text-xs text-gray-300 shrink-0">至</span>
        <input type="text" value="23:59" readonly class="w-full bg-gray-200 text-gray-500 px-3 py-2 rounded text-sm text-center select-none">
      </div>
    </div>

    <button type="submit" class="w-full bg-[#1D4ED8] hover:bg-blue-700 text-white font-bold py-2.5 rounded text-sm transition-colors cursor-pointer">
      查詢
    </button>
    
  </form>

  {% if error_msg %}
    <div class="w-full max-w-md bg-red-100 border border-red-400 text-red-700 p-3 rounded text-sm shadow">
      <p class="font-bold">❌ 狀態提示：</p>
      <p class="text-xs mt-1 bg-white p-2 rounded font-mono">{{ error_msg }}</p>
    </div>
  {% endif %}

  {% if train_data is not none %}
    <div class="w-full max-w-md bg-white p-4 rounded-lg shadow-lg">
      <h3 class="text-gray-800 font-bold mb-3 border-b pb-2 text-sm">查詢結果 (當日直達車)</h3>
      <div class="space-y-2 max-h-72 overflow-y-auto text-sm text-gray-700">
        {% if train_data|length == 0 %}
          <div class="text-center py-4 text-gray-400">當日該區間無直達車次。</div>
        {% else %}
          {% for train in train_data %}
            <div class="flex justify-between items-center p-2 border-b border-gray-100 hover:bg-gray-50">
              <div>
                <span class="font-bold text-blue-600">{{ train.DailyTrainInfo.TrainTypeName.Zh_tw }}</span> 
                <span class="text-xs text-gray-400">({{ train.DailyTrainInfo.TrainNo }} 次)</span>
              </div>
              <div class="font-mono font-medium text-gray-800">
                {{ train.StopTimes[0].DepartureTime }} ➔ {{ train.StopTimes[1].ArrivalTime }}
              </div>
            </div>
          {% endfor %}
        {% endif %}
      </div>
    </div>
  {% endif %}

  <script>
    function swapStations() {
      const start = document.getElementById('start_station');
      const end = document.getElementById('end_station');
      const temp = start.value; start.value = end.value; end.value = temp;
    }

    function toggleTimeType(type) {
      document.getElementById('time_type').value = type;
      const btnDept = document.getElementById('btn_dept'); const btnArr = document.getElementById('btn_arr');
      if (type === 'departure') {
        btnDept.className = "flex-1 bg-[#1D4ED8] py-1.5 text-center font-medium cursor-pointer";
        btnArr.className = "flex-1 bg-[#4B5563] py-1.5 text-center text-gray-300 hover:bg-gray-500 cursor-pointer";
      } else {
        btnDept.className = "flex-1 bg-[#4B5563] py-1.5 text-center text-gray-300 hover:bg-gray-500 cursor-pointer";
        btnArr.className = "flex-1 bg-[#1D4ED8] py-1.5 text-center font-medium cursor-pointer";
      }
    }
  </script>
</body>
</html>
"""

def get_tdx_token():
    """新制 OIDC 專用核心驗證通道"""
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    
    c_id = CLIENT_ID.strip() if CLIENT_ID else ""
    c_secret = CLIENT_SECRET.strip() if CLIENT_SECRET else ""
    
    if not c_id or not c_secret:
        return None, "環境變數讀取失敗：請檢查 Vercel 的 TDX_CLIENT_ID 與 TDX_CLIENT_SECRET 是否有填寫並完成 Redeploy。"

    payload = {
        'grant_type': 'client_credentials',
        'client_id': c_id,
        'client_secret': c_secret
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(auth_url, data=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get('access_token'), None
        else:
            return None, f"Token 伺服器拒絕 (HTTP {response.status_code}) - 內容：{response.text}"
    except Exception as e:
        return None, f"連線驗證伺服器發生異常: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    train_data = None
    error_msg = None
    form_data = {'start_station': '1000', 'end_station': '3300', 'search_date': '2026-05-27', 'time_type': 'departure'}

    if request.method == 'POST':
        form_data['start_station'] = request.form.get('start_station')
        form_data['end_station'] = request.form.get('end_station')
        form_data['search_date'] = request.form.get('search_date')
        form_data['time_type'] = request.form.get('time_type')

        token, api_error = get_tdx_token()
        
        if token:
            # 🎯 【關鍵修正】移除了不必要的 /From/ 欄位，還原官方標準 V3 起訖站時刻表網址結構
            api_url = f"https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/DailyTrainTimetable/OD/{form_data['start_station']}/To/{form_data['end_station']}/{form_data['search_date']}?$format=JSON"
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
            try:
                api_res = requests.get(api_url, headers=headers, timeout=10)
                if api_res.status_code == 200:
                    raw_data = api_res.json().get('TrainTimetables', [])
                    train_data = sorted(raw_data, key=lambda x: x['StopTimes'][0]['DepartureTime'])
                else:
                    error_msg = f"時刻表查詢失敗 (HTTP {api_res.status_code}): {api_res.text}"
            except Exception as e:
                error_msg = f"API 連線異常: {e}"
        else:
            error_msg = api_error

    return render_template_string(HTML_TEMPLATE, train_data=train_data, error_msg=error_msg, form_data=form_data)

app.debug = True