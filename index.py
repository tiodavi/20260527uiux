import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# 🔑 2026 新制 OIDC 核心：將你的 Client Id 當作 API Key 使用
# 請點擊「管理」，完整複製 Client Id（包含 tioplato001- 開頭與後面的隨機碼）
TDX_API_KEY = os.environ.get('TDX_API_KEY', 'tioplato001-4436c997-a725-410c')

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
      <span class="text-sm font-bold">列車時刻查詢 (2026 終極金鑰版)</span>
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
      <p class="font-bold">❌ 查詢狀態提示：</p>
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

        # 🎯 呼叫台鐵時刻表 API
        api_url = f"https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/DailyTrainTimetable/OD/From/{form_data['start_station']}/To/{form_data['end_station']}/{form_data['search_date']}?$format=JSON"
        
        api_key = TDX_API_KEY.strip() if TDX_API_KEY else ""

        if not api_key or "你的" in api_key:
            error_msg = "配置失敗：請將 TDX 平台上完整的 Client Id 填入程式的 TDX_API_KEY 中。"
        else:
            try:
                # 🚀 2026 終極解法：將 Client Id 當作萬用密鑰，直接放入 x-api-key 標頭
                headers = {
                    'x-api-key': api_key,
                    'Accept': 'application/json'
                }
                
                api_res = requests.get(api_url, headers=headers, timeout=10)
                
                if api_res.status_code == 200:
                    raw_data = api_res.json().get('TrainTimetables', [])
                    train_data = sorted(raw_data, key=lambda x: x['StopTimes'][0]['DepartureTime'])
                else:
                    error_msg = f"API 連線失敗 (HTTP {api_res.status_code})。錯誤內容：{api_res.text}"
            except Exception as e:
                error_msg = f"網路連線異常: {e}"

    return render_template_string(HTML_TEMPLATE, train_data=train_data, error_msg=error_msg, form_data=form_data)

app.debug = True