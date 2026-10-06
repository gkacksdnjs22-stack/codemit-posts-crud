from pathlib import Path

source = Path('C:/Users/User/OneDrive/문서/ChatGPT/aleph 과제/escape-map/tools/generate_floor_plans.py')
namespace = {}
definitions = source.read_text(encoding='utf-8').split('\nfor floor in FLOORS:')[0]
exec(definitions.replace("OUT.mkdir(parents=True, exist_ok=True)", ""), namespace)
floors = namespace['FLOORS']
floors[0]['stairs'] = []
floors[0]['rooms'][0] = (-20,-17,7,15,'기존 계단실 영역','utility')
floors[0]['notes'] = ['1층에서 내려가는 계단은 제거되었습니다.', '현실 3층 전용 승강기 연결은 후속 설계입니다.']
floors[1]['stairs'] = [(-18.65,-13.5,'보조 계단','1F ↔ 2F',1.8)]
floors[1]['notes'] = ['지하계단 제거 위치는 연속 바닥으로 연결되었습니다.', '중앙 계단과 기존 1층 방 배치를 보존합니다.']
floors[2]['stairs'] = [(-18.65,-13.5,'숨겨진 계단','2F → 이공간 전환점',1.8)]
floors[2]['rooms'][0] = (-20,-17,4,7,'비밀 진입 구역','utility')
floors[2]['notes'] = ['독서 라운지 북측 벽 패널에 숨겨진 문이 있습니다.', '문 좌표 X -18.65 / Z -10, 폭 1.8m.', '계단 상단은 현실 3층 방에 연결하지 않습니다.']
floors[3]['stairs'] = []
floors[3]['subtitle'] = '현재 잔존 구조 · 현실 3층 재설계 예정'
floors[3]['notes'] = ['기존 방 구획의 기록이며 확정 설계가 아닙니다.', '2층 비밀계단과 기존 3층 방은 직접 연결되지 않습니다.']
out = Path(__file__).parent / 'static' / 'captures' / 'plans'
out.mkdir(parents=True, exist_ok=True)
for floor in floors:
    svg = namespace['plan'](floor)
    if floor['id'] == '2f':
        svg = svg.replace('</svg>', '<circle cx="143.75" cy="350" r="12" fill="#794c70"/><text x="170" y="350" font-family="Malgun Gothic" font-size="15" fill="#794c70">숨겨진 벽문</text></svg>')
    (out / (floor['id'] + '.svg')).write_text(svg, encoding='utf-8')
print('Generated B1, 1F, 2F, 3F plans with current route annotations.')
