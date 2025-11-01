import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
from datetime import datetime
import replicate
import os
import random

# 페이지 설정
st.set_page_config(
    page_title="헤어스타일 모델 생성기 v3",
    page_icon="💇",
    layout="wide"
)

# 세션 상태 초기화
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'api_provider' not in st.session_state:
    st.session_state.api_provider = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'history' not in st.session_state:
    st.session_state.history = []

# CSS 스타일 (Navy & Gold Premium Theme)
st.markdown("""
<style>
    /* 전역 배경색 */
    .stApp {
        background-color: #0A1628;
    }
    
    /* 메인 헤더 - Navy & Gold 테마 */
    .main-header {
        text-align: center;
        padding: 2.5rem 0;
        background: linear-gradient(135deg, #0F2240 0%, #0A1628 100%);
        color: #ffffff;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid rgba(201, 169, 98, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(201, 169, 98, 0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .main-header h1 {
        color: #C9A962;
        text-shadow: 0 2px 10px rgba(201, 169, 98, 0.3);
        position: relative;
        z-index: 1;
    }
    
    /* 옵션 카드 */
    .option-card {
        background: rgba(30, 58, 95, 0.6);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid rgba(201, 169, 98, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .option-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(201, 169, 98, 0.3);
        border-color: #C9A962;
        background: rgba(30, 58, 95, 0.8);
    }
    
    /* 경고 박스 - Navy & Gold */
    .warning-box {
        background: rgba(201, 169, 98, 0.15);
        border-left: 4px solid #C9A962;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 8px;
        color: #ffffff;
        backdrop-filter: blur(10px);
    }
    
    /* 정보 박스 - Navy & Blue */
    .info-box {
        background: rgba(74, 144, 226, 0.15);
        border-left: 4px solid #4A90E2;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 8px;
        color: #ffffff;
        backdrop-filter: blur(10px);
    }
    
    /* 버튼 스타일 - Gold 그라디언트 */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #C9A962 0%, #A68B4E 100%);
        color: #0A1628;
        border: none;
        padding: 0.85rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(201, 169, 98, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #D4B76E 0%, #C9A962 100%);
        box-shadow: 0 6px 25px rgba(201, 169, 98, 0.5);
        transform: translateY(-2px);
    }
    
    /* Provider Badge */
    .provider-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 0.5rem;
        border: 1px solid rgba(201, 169, 98, 0.3);
    }
    
    .badge-google {
        background: rgba(74, 144, 226, 0.2);
        color: #4A90E2;
        border-color: #4A90E2;
    }
    
    .badge-replicate {
        background: rgba(201, 169, 98, 0.2);
        color: #C9A962;
        border-color: #C9A962;
    }
    /* 프롬프트 라이브러리 플로팅 버튼 - Navy & Gold */
    .prompt-library-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        background: linear-gradient(135deg, #C9A962 0%, #A68B4E 100%);
        color: #0A1628;
        padding: 15px 28px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0 6px 25px rgba(201, 169, 98, 0.5);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 10px;
        border: 2px solid rgba(201, 169, 98, 0.3);
    }
    
    .prompt-library-btn:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 35px rgba(201, 169, 98, 0.7);
        background: linear-gradient(135deg, #D4B76E 0%, #C9A962 100%);
        text-decoration: none;
        color: #0A1628;
        border-color: #C9A962;
    }
    
    .prompt-library-btn::before {
        content: "📚";
        font-size: 22px;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
    }
    
    /* Streamlit 기본 요소 스타일 오버라이드 */
    .stTextInput>div>div>input {
        background-color: rgba(30, 58, 95, 0.6) !important;
        color: #ffffff !important;
        border: 1px solid rgba(201, 169, 98, 0.3) !important;
        border-radius: 8px !important;
    }
    
    .stTextArea>div>div>textarea {
        background-color: rgba(30, 58, 95, 0.6) !important;
        color: #ffffff !important;
        border: 1px solid rgba(201, 169, 98, 0.3) !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox>div>div>div {
        background-color: rgba(30, 58, 95, 0.6) !important;
        color: #ffffff !important;
        border: 1px solid rgba(201, 169, 98, 0.3) !important;
    }
    
    .stExpander {
        background-color: rgba(30, 58, 95, 0.4) !important;
        border: 1px solid rgba(201, 169, 98, 0.2) !important;
        border-radius: 10px !important;
    }
    
    .stExpander summary {
        color: #C9A962 !important;
        font-weight: bold !important;
    }
    
    /* 파일 업로더 */
    .stFileUploader>div>div {
        background-color: rgba(30, 58, 95, 0.6) !important;
        border: 2px dashed rgba(201, 169, 98, 0.4) !important;
        border-radius: 10px !important;
    }
    
    /* 슬라이더 */
    .stSlider>div>div>div>div {
        background-color: #C9A962 !important;
    }
    
    /* 체크박스 */
    .stCheckbox>label {
        color: #ffffff !important;
    }
    
    /* 라벨 색상 */
    label {
        color: #C9A962 !important;
        font-weight: 500 !important;
    }
    
    /* 캡션 */
    .caption {
        color: rgba(201, 169, 98, 0.7) !important;
    }
    
    /* 성공 메시지 */
    .stSuccess {
        background-color: rgba(74, 144, 226, 0.2) !important;
        color: #4A90E2 !important;
        border-left: 4px solid #4A90E2 !important;
    }
    
    /* 에러 메시지 */
    .stError {
        background-color: rgba(201, 169, 98, 0.2) !important;
        color: #C9A962 !important;
        border-left: 4px solid #C9A962 !important;
    }
    
    /* 배경 장식 원형 */
    .stApp::before {
        content: '';
        position: fixed;
        top: -300px;
        right: -300px;
        width: 800px;
        height: 800px;
        background: radial-gradient(circle, rgba(15, 34, 64, 0.6) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
    }
    
    .stApp::after {
        content: '';
        position: fixed;
        bottom: -400px;
        left: -400px;
        width: 1000px;
        height: 1000px;
        background: radial-gradient(circle, rgba(15, 34, 64, 0.4) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
    }

    /* 전역 여백 개선 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 섹션 간격 */
    .stMarkdown {
        margin-bottom: 0.5rem;
    }
    
    /* 버튼 그룹 간격 */
    .stButton > button {
        margin: 0.25rem 0;
    }
    
    /* Expander 여백 */
    .streamlit-expanderHeader {
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* 입력 필드 간격 */
    .stTextInput, .stTextArea, .stSelectbox, .stSlider {
        margin-bottom: 1rem;
    }
    
    /* 깔끔한 구분선 */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

</style>
""", unsafe_allow_html=True)

# 프롬프트 라이브러리 플로팅 버튼
st.markdown("""
<a href="http://prompt.grow-up.kr/" target="_blank" class="prompt-library-btn">
    프롬프트
</a>
""", unsafe_allow_html=True)


# ========== 고급 옵션 렌더링 함수들 ==========

def render_advanced_options():
    """고급 설정 UI"""
    with st.expander("⚙️ 고급 설정", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # 해상도
            resolution = st.selectbox(
                "📐 해상도",
                ["1024x1024 (기본)", "2048x2048 (2K)", "4096x4096 (4K)"],
                index=0,
                help="해상도 선택"
            )
            
            # 이미지 수 (2x2 그리드)
            st.markdown("🖼️ **생성 이미지 수**")
            
            # 세션 상태 초기화
            if 'num_images_selected' not in st.session_state:
                st.session_state.num_images_selected = 1
            
            grid_col1, grid_col2 = st.columns(2)
            
            with grid_col1:
                if st.button("1장", key="img_1", use_container_width=True, 
                           type="primary" if st.session_state.num_images_selected == 1 else "secondary"):
                    st.session_state.num_images_selected = 1
                    st.rerun()
                
                if st.button("3장", key="img_3", use_container_width=True,
                           type="primary" if st.session_state.num_images_selected == 3 else "secondary"):
                    st.session_state.num_images_selected = 3
                    st.rerun()
            
            with grid_col2:
                if st.button("2장", key="img_2", use_container_width=True,
                           type="primary" if st.session_state.num_images_selected == 2 else "secondary"):
                    st.session_state.num_images_selected = 2
                    st.rerun()
                
                if st.button("4장", key="img_4", use_container_width=True,
                           type="primary" if st.session_state.num_images_selected == 4 else "secondary"):
                    st.session_state.num_images_selected = 4
                    st.rerun()
            
            num_images = st.session_state.num_images_selected
            st.markdown(f"<p style='text-align: center; color: #C9A962;'>선택됨: {num_images}장</p>", unsafe_allow_html=True)
            
            # 프롬프트 강도
            guidance_scale = st.slider(
                "프롬프트 강도",
                min_value=1.0,
                max_value=20.0,
                value=7.5,
                step=0.5,
                help="프롬프트 충실도"
            )
        
        with col2:
            # Seed 설정
            use_random_seed = st.checkbox("랜덤 Seed", value=True)
            if use_random_seed:
                seed = random.randint(0, 999999999)
                st.text_input("Seed (자동 생성)", value=str(seed), disabled=True, key="seed_display")
            else:
                seed = st.number_input(
                    "Seed (고정)",
                    min_value=0,
                    max_value=999999999,
                    value=12345,
                    help="재현성 확보"
                )
            
            # 샘플링 단계
            steps = st.slider(
                "샘플링 단계",
                min_value=20,
                max_value=100,
                value=50,
                step=5,
                help="생성 품질"
            )
        
        # 네거티브 프롬프트
        negative_prompt = st.text_area(
            "네거티브 프롬프트 (제외할 요소)",
            value="blurry, low quality, distorted, deformed, ugly, bad anatomy",
            height=80,
            help="제외할 요소"
        )
    
    return {
        "resolution": resolution,
        "num_images": num_images,
        "guidance_scale": guidance_scale,
        "seed": seed,
        "steps": steps,
        "negative_prompt": negative_prompt
    }


def render_face_refinement():
    """얼굴 세부 조정 UI"""
    with st.expander("얼굴 조정", expanded=False):
        st.markdown("슬라이더로 얼굴 특징을 미세 조정합니다")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**눈**")
            eye_size = st.slider("눈 크기", -100, 100, 0, key="eye")
            eye_distance = st.slider("눈 간격", -100, 100, 0, key="eye_dist")
        
        with col2:
            st.markdown("**코/입**")
            nose_size = st.slider("코 크기", -100, 100, 0, key="nose")
            mouth_size = st.slider("입 크기", -100, 100, 0, key="mouth")
        
        with col3:
            st.markdown("**전체**")
            face_width = st.slider("얼굴 폭", -100, 100, 0, key="face_w")
            face_length = st.slider("얼굴 길이", -100, 100, 0, key="face_l")
        
        st.markdown("---")
        
        col4, col5 = st.columns(2)
        with col4:
            skin_smoothness = st.slider("피부 매끄러움", 0, 100, 50, key="skin")
        with col5:
            brightness = st.slider("💡 밝기", -100, 100, 0, key="bright")
    
    return {
        "eye_size": eye_size,
        "eye_distance": eye_distance,
        "nose_size": nose_size,
        "mouth_size": mouth_size,
        "face_width": face_width,
        "face_length": face_length,
        "skin_smoothness": skin_smoothness,
        "brightness": brightness
    }


# ============ 뷰티 프리셋 시스템 ============

BEAUTY_PRESETS = {
    "자연스러운 보정": {
        "makeup_type": "natural",
        "whitening": 30,
        "skin_texture": 60,
        "glow_effect": 40,
        "makeup_intensity": 50,
        "retouch_areas": ["전체 얼굴", "피부톤"],
        "remove_blemish": True,
        "natural_look": True,
        "enhance_eyes": False,
        "plump_lips": False
    },
    "화려한 메이크업": {
        "makeup_type": "full",
        "whitening": 70,
        "skin_texture": 80,
        "glow_effect": 30,
        "makeup_intensity": 85,
        "retouch_areas": ["전체 얼굴", "눈 화장", "입술 화장", "볼 홍조", "하이라이트", "음영/쉐딩"],
        "remove_blemish": True,
        "natural_look": False,
        "enhance_eyes": True,
        "plump_lips": True
    },
    "K-Beauty 물광": {
        "makeup_type": "dewy",
        "whitening": 50,
        "skin_texture": 90,
        "glow_effect": 85,
        "makeup_intensity": 40,
        "retouch_areas": ["전체 얼굴", "피부톤", "하이라이트"],
        "remove_blemish": True,
        "natural_look": True,
        "enhance_eyes": False,
        "plump_lips": False
    }
}


def save_custom_preset(preset_name, beauty_options):
    """커스텀 뷰티 프리셋 저장"""
    if 'custom_beauty_presets' not in st.session_state:
        st.session_state.custom_beauty_presets = {}
    
    st.session_state.custom_beauty_presets[preset_name] = beauty_options.copy()


def load_preset(preset_name):
    """프리셋 불러오기 (기본 또는 커스텀)"""
    # 기본 프리셋 확인
    if preset_name in BEAUTY_PRESETS:
        return BEAUTY_PRESETS[preset_name].copy()
    
    # 커스텀 프리셋 확인
    if 'custom_beauty_presets' in st.session_state:
        if preset_name in st.session_state.custom_beauty_presets:
            return st.session_state.custom_beauty_presets[preset_name].copy()
    
    return None


def analyze_face_for_optimization(image):
    """
    AI가 얼굴을 분석해서 최적의 뷰티 보정값 추천
    Gemini Vision API 사용
    """
    try:
        genai.configure(api_key=st.session_state.api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        analysis_prompt = """
Analyze this portrait photo and recommend optimal beauty retouch settings.

Analyze:
1. Skin condition (brightness, smoothness, blemishes)
2. Current makeup level (none/light/medium/heavy)
3. Skin tone (fair/medium/tan)
4. Face features that could be enhanced

Provide recommendations in this exact JSON format:
{
  "makeup_type": "natural" or "full" or "dewy",
  "whitening": 0-100,
  "skin_texture": 0-100,
  "glow_effect": 0-100,
  "makeup_intensity": 0-100,
  "retouch_areas": ["전체 얼굴", "피부톤", etc],
  "remove_blemish": true/false,
  "enhance_eyes": true/false,
  "plump_lips": true/false,
  "reasoning": "brief explanation"
}

Recommendations should be subtle and natural unless the photo already has heavy makeup.
"""
        
        response = model.generate_content([analysis_prompt, image])
        
        # JSON 추출
        import json
        import re
        
        response_text = response.text
        
        # JSON 블록 찾기
        json_match = re.search(r'```json\s*({.*?})\s*```', response_text, re.DOTALL)
        if not json_match:
            json_match = re.search(r'({.*?})', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
            recommendations = json.loads(json_str)
            
            # 기본값 설정
            default_options = {
                "makeup_type": "natural",
                "whitening": 30,
                "skin_texture": 60,
                "glow_effect": 40,
                "makeup_intensity": 50,
                "retouch_areas": ["전체 얼굴", "피부톤"],
                "remove_blemish": True,
                "natural_look": True,
                "enhance_eyes": False,
                "plump_lips": False,
                "reasoning": "기본 설정"
            }
            
            # 추천값으로 업데이트
            default_options.update(recommendations)
            default_options['natural_look'] = True  # 항상 자연스러움 유지
            
            return default_options
        else:
            return None
            
    except Exception as e:
        st.error(f"얼굴 분석 실패: {str(e)}")
        return None


def render_preset_manager():
    """뷰티 프리셋 관리 UI"""
    st.markdown("### 📚 뷰티 프리셋")
    
    # 프리셋 선택
    preset_col1, preset_col2 = st.columns([3, 1])
    
    with preset_col1:
        # 기본 프리셋 + 커스텀 프리셋 목록
        all_presets = list(BEAUTY_PRESETS.keys())
        if 'custom_beauty_presets' in st.session_state:
            all_presets.extend(list(st.session_state.custom_beauty_presets.keys()))
        
        selected_preset = st.selectbox(
            "프리셋 선택",
            ["직접 설정"] + all_presets,
            help="저장된 뷰티 설정을 빠르게 불러올 수 있습니다"
        )
    
    with preset_col2:
        if selected_preset != "직접 설정":
            if st.button("🔄 적용", use_container_width=True):
                preset_data = load_preset(selected_preset)
                if preset_data:
                    # session_state에 저장
                    for key, value in preset_data.items():
                        st.session_state[f"beauty_{key}"] = value
                    st.success(f"✅ '{selected_preset}' 적용 완료!")
                    st.rerun()
    
    # 현재 설정 저장
    st.markdown("---")
    save_col1, save_col2 = st.columns([3, 1])
    
    with save_col1:
        new_preset_name = st.text_input(
            "새 프리셋 이름",
            placeholder="예: 내 스타일",
            key="new_preset_name"
        )
    
    with save_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 저장", use_container_width=True, disabled=not new_preset_name):
            # 현재 뷰티 설정 수집
            current_settings = {
                "makeup_type": st.session_state.get('makeup_type', 'natural'),
                "whitening": st.session_state.get('beauty_whitening', 30),
                "skin_texture": st.session_state.get('beauty_skin_texture', 60),
                "glow_effect": st.session_state.get('beauty_glow_effect', 40),
                "makeup_intensity": st.session_state.get('beauty_makeup_intensity', 50),
                "retouch_areas": st.session_state.get('beauty_retouch_areas', ["전체 얼굴", "피부톤"]),
                "remove_blemish": st.session_state.get('beauty_remove_blemish', True),
                "natural_look": st.session_state.get('beauty_natural_look', True),
                "enhance_eyes": st.session_state.get('beauty_enhance_eyes', False),
                "plump_lips": st.session_state.get('beauty_plump_lips', False)
            }
            save_custom_preset(new_preset_name, current_settings)
            st.success(f"✅ '{new_preset_name}' 저장 완료!")
            st.rerun()


def render_beauty_retouch():
    """뷰티 보정 UI (Refine AI 스타일 - 좌우 2열 레이아웃)"""
    with st.expander("💄 뷰티 보정", expanded=False):
        # 프리셋 매니저
        render_preset_manager()
        
        st.markdown("---")
        
        # 메인 레이아웃: 왼쪽 컨트롤, 오른쪽 정보/미리보기
        left_col, right_col = st.columns([2, 1])
        
        with left_col:
            # 메이크업 타입 선택
            st.markdown("#### 메이크업 타입")
            makeup_cols = st.columns(3)
            
            with makeup_cols[0]:
                natural_retouch = st.button("보정 메이크업", key="natural_makeup", use_container_width=True)
            with makeup_cols[1]:
                full_makeup = st.button("풀 메이크업", key="full_makeup", use_container_width=True)
            with makeup_cols[2]:
                dewy_skin = st.button("물광 피부", key="dewy_skin", use_container_width=True)
            
            # 선택된 메이크업 타입 저장
            if 'makeup_type' not in st.session_state:
                st.session_state.makeup_type = "natural"
            
            if natural_retouch:
                st.session_state.makeup_type = "natural"
            elif full_makeup:
                st.session_state.makeup_type = "full"
            elif dewy_skin:
                st.session_state.makeup_type = "dewy"
            
            # 현재 선택된 타입 표시
            makeup_type_names = {
                "natural": "보정 메이크업",
                "full": "풀 메이크업",
                "dewy": "물광 피부"
            }
            st.info(f"{makeup_type_names[st.session_state.makeup_type]}")
            
            st.markdown("---")
            
            # 피부 보정 슬라이더
            st.markdown("#### 피부 보정")
            
            # 화이트닝
            whitening = st.slider(
                "피부 화이트닝",
                0, 100, 
                st.session_state.get('beauty_whitening', 30),
                help="피부 밝기",
                key="slider_whitening"
            )
            
            # 피부 매끄러움
            skin_texture = st.slider(
                "피부 매끄러움",
                0, 100, 
                st.session_state.get('beauty_skin_texture', 60),
                help="피부 질감",
                key="slider_skin_texture"
            )
            
            # 물광 효과
            glow_effect = st.slider(
                "물광 효과",
                0, 100, 
                st.session_state.get('beauty_glow_effect', 40),
                help="광택 효과",
                key="slider_glow_effect"
            )
            
            # 화장 농도
            makeup_intensity = st.slider(
                "화장 농도",
                0, 100, 
                st.session_state.get('beauty_makeup_intensity', 50),
                help="메이크업 강도",
                key="slider_makeup_intensity"
            )
            
            st.markdown("---")
            
            # 보정 부위 선택
            st.markdown("#### 보정 부위")
            
            retouch_areas = st.multiselect(
                "보정할 영역을 선택하세요",
                [
                    "전체 얼굴",
                    "피부톤",
                    "눈 화장",
                    "입술 화장",
                    "볼 홍조",
                    "하이라이트",
                    "음영/쉐딩"
                ],
                default=st.session_state.get('beauty_retouch_areas', ["전체 얼굴", "피부톤"]),
                key="multiselect_retouch_areas"
            )
            
            st.markdown("---")
            
            # 추가 옵션
            st.markdown("#### 추가 옵션")
            
            option_col1, option_col2 = st.columns(2)
            
            with option_col1:
                remove_blemish = st.checkbox("잡티 제거", value=st.session_state.get('beauty_remove_blemish', True), key="cb_remove_blemish")
                natural_look = st.checkbox("자연스러운 느낌 유지", value=st.session_state.get('beauty_natural_look', True), key="cb_natural_look")
            
            with option_col2:
                enhance_eyes = st.checkbox("눈매 강조", value=st.session_state.get('beauty_enhance_eyes', False), key="cb_enhance_eyes")
                plump_lips = st.checkbox("입술 볼륨감", value=st.session_state.get('beauty_plump_lips', False), key="cb_plump_lips")
        
        with right_col:
            # AI 자동 최적화
            st.markdown("#### ✨ AI 자동 최적화")
            st.markdown("사진을 업로드하면 AI가 최적값을 추천합니다")
            
            face_image_for_analysis = st.file_uploader(
                "얼굴 사진 업로드",
                type=['png', 'jpg', 'jpeg'],
                key="face_analysis_upload",
                help="분석할 사진 업로드",
                label_visibility="collapsed"
            )
            
            analyze_button = st.button("AI 분석", use_container_width=True, disabled=not face_image_for_analysis)
            
            if analyze_button and face_image_for_analysis:
                with st.spinner("🔍 AI가 얼굴을 분석 중..."):
                    from PIL import Image
                    image = Image.open(face_image_for_analysis)
                    
                    recommendations = analyze_face_for_optimization(image)
                    
                    if recommendations:
                        st.success("분석 완료")
                        
                        # 추천 이유 표시
                        if 'reasoning' in recommendations:
                            st.info(f"💡 {recommendations['reasoning']}")
                        
                        # 추천값을 session_state에 저장
                        st.session_state.makeup_type = recommendations.get('makeup_type', 'natural')
                        st.session_state.beauty_whitening = recommendations.get('whitening', 30)
                        st.session_state.beauty_skin_texture = recommendations.get('skin_texture', 60)
                        st.session_state.beauty_glow_effect = recommendations.get('glow_effect', 40)
                        st.session_state.beauty_makeup_intensity = recommendations.get('makeup_intensity', 50)
                        st.session_state.beauty_retouch_areas = recommendations.get('retouch_areas', ["전체 얼굴", "피부톤"])
                        st.session_state.beauty_remove_blemish = recommendations.get('remove_blemish', True)
                        st.session_state.beauty_enhance_eyes = recommendations.get('enhance_eyes', False)
                        st.session_state.beauty_plump_lips = recommendations.get('plump_lips', False)
                        
                        st.rerun()
                    else:
                        st.warning("분석 실패")
            
            st.markdown("---")
            
            # 현재 설정 요약
            st.markdown("#### 📋 현재 설정")
            st.markdown(f"**메이크업**: {makeup_type_names[st.session_state.makeup_type]}")
            st.markdown(f"**화이트닝**: {whitening}")
            st.markdown(f"**매끄러움**: {skin_texture}")
            st.markdown(f"**물광**: {glow_effect}")
            st.markdown(f"**화장 농도**: {makeup_intensity}")
    
    return {
        "makeup_type": st.session_state.makeup_type,
        "whitening": whitening,
        "skin_texture": skin_texture,
        "glow_effect": glow_effect,
        "makeup_intensity": makeup_intensity,
        "retouch_areas": retouch_areas,
        "remove_blemish": remove_blemish,
        "natural_look": natural_look,
        "enhance_eyes": enhance_eyes,
        "plump_lips": plump_lips
    }


def beauty_options_to_prompt(beauty_options):
    """
    뷰티 보정 옵션을 자연어 프롬프트로 변환
    
    Args:
        beauty_options (dict): render_beauty_retouch()에서 반환된 옵션 딕셔너리
    
    Returns:
        str: 변환된 프롬프트 텍스트
    """
    if not beauty_options:
        return ""
    
    prompt_parts = []
    
    # 1. 메이크업 타입 변환
    makeup_type_map = {
        "retouch": "natural beauty retouch with subtle enhancements",
        "full": "full glam makeup with defined features and vibrant colors",
        "dewy": "dewy glass skin effect with luminous glow and fresh complexion"
    }
    makeup_type = beauty_options.get("makeup_type", "retouch")
    prompt_parts.append(makeup_type_map.get(makeup_type, makeup_type_map["retouch"]))
    
    # 2. 피부 화이트닝 강도 변환
    whitening = beauty_options.get("whitening", 0)
    if whitening > 0:
        if whitening >= 70:
            prompt_parts.append("strong skin brightening with porcelain-white complexion")
        elif whitening >= 40:
            prompt_parts.append("moderate skin brightening for a fair and radiant look")
        else:
            prompt_parts.append("subtle skin brightening maintaining natural tone")
    
    # 3. 피부 매끄러움 변환
    skin_texture = beauty_options.get("skin_texture", 0)
    if skin_texture > 0:
        if skin_texture >= 70:
            prompt_parts.append("extremely smooth and flawless skin texture, airbrushed finish")
        elif skin_texture >= 40:
            prompt_parts.append("smooth and refined skin texture with soft appearance")
        else:
            prompt_parts.append("slightly smoothed skin maintaining natural texture")
    
    # 4. 물광 효과 변환
    glow_effect = beauty_options.get("glow_effect", 0)
    if glow_effect > 0:
        if glow_effect >= 70:
            prompt_parts.append("intense dewy glow with wet-look luminosity and glossy finish")
        elif glow_effect >= 40:
            prompt_parts.append("moderate dewy glow with natural moisture and light reflection")
        else:
            prompt_parts.append("subtle dewy effect with gentle luminosity")
    
    # 5. 화장 농도 변환
    makeup_intensity = beauty_options.get("makeup_intensity", 50)
    if makeup_intensity >= 70:
        prompt_parts.append("heavy makeup intensity with bold and dramatic look")
    elif makeup_intensity >= 40:
        prompt_parts.append("medium makeup intensity with balanced and defined features")
    elif makeup_intensity > 0:
        prompt_parts.append("light makeup intensity with natural and fresh appearance")
    
    # 6. 보정 부위 변환
    retouch_areas = beauty_options.get("retouch_areas", [])
    if retouch_areas:
        area_prompts = []
        
        if "전체 얼굴" in retouch_areas:
            area_prompts.append("overall facial enhancement")
        if "피부톤" in retouch_areas:
            area_prompts.append("even skin tone correction")
        if "눈 화장" in retouch_areas:
            area_prompts.append("enhanced eye makeup with defined lashes and eyeshadow")
        if "입술 화장" in retouch_areas:
            area_prompts.append("enhanced lip color with natural volume")
        if "볼 홍조" in retouch_areas:
            area_prompts.append("soft cheek blush with rosy glow")
        if "하이라이트" in retouch_areas:
            area_prompts.append("subtle highlight on cheekbones, nose bridge, and cupid's bow")
        if "음영/쉐딩" in retouch_areas:
            area_prompts.append("natural contouring and shading for dimension")
        
        if area_prompts:
            prompt_parts.append(f"Focus on: {', '.join(area_prompts)}")
    
    # 7. 추가 옵션 변환
    additional_features = []
    
    if beauty_options.get("remove_blemish", False):
        additional_features.append("blemish-free clear skin")
    
    if beauty_options.get("natural_look", False):
        additional_features.append("maintaining natural appearance and realistic texture")
    
    if beauty_options.get("enhance_eyes", False):
        additional_features.append("enhanced eye definition with larger and brighter eyes")
    
    if beauty_options.get("plump_lips", False):
        additional_features.append("fuller and plumper lips with soft volume")
    
    if additional_features:
        prompt_parts.append(", ".join(additional_features))
    
    # 최종 프롬프트 조합
    final_prompt = ". ".join(prompt_parts)
    
    # 전체적으로 자연스러운 프롬프트가 되도록 마무리
    if final_prompt:
        final_prompt += ". Professional beauty photography, high quality, detailed facial features."
    
    return final_prompt


def render_lighting_options():
    """조명 설정 UI"""
    with st.expander("조명 설정", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            lighting_type = st.selectbox(
                "조명 타입",
                [
                    "자연광 (Natural Light)",
                    "스튜디오 조명 (Studio)",
                    "소프트박스 (Softbox)",
                    "링라이트 (Ring Light)",
                    "극적인 조명 (Dramatic)",
                    "황금빛 (Golden Hour)"
                ],
                index=1
            )
            
            lighting_intensity = st.slider(
                "조명 강도",
                0, 100, 70,
                help="밝기"
            )
        
        with col2:
            lighting_direction = st.selectbox(
                "조명 방향",
                [
                    "정면 (Frontal)",
                    "45도 위 (45° High)",
                    "측면 (Side)",
                    "백라이트 (Backlight)",
                    "상단 (Top)"
                ],
                index=0
            )
            
            shadow_strength = st.slider(
                "그림자 강도",
                0, 100, 30,
                help="그림자의 진하기를 조절합니다"
            )
        
        # 추가 옵션
        col3, col4 = st.columns(2)
        with col3:
            contrast = st.slider("대비", -50, 50, 0)
        with col4:
            saturation = st.slider("채도", -50, 50, 0)
    
    return {
        "lighting_type": lighting_type,
        "lighting_intensity": lighting_intensity,
        "lighting_direction": lighting_direction,
        "shadow_strength": shadow_strength,
        "contrast": contrast,
        "saturation": saturation
    }


# ========== 옵션을 프롬프트로 변환하는 함수들 ==========

def face_options_to_prompt(face_opts):
    """얼굴 옵션을 프롬프트 텍스트로 변환"""
    prompt_parts = []
    
    # 눈
    if face_opts['eye_size'] > 30:
        prompt_parts.append("large expressive eyes")
    elif face_opts['eye_size'] < -30:
        prompt_parts.append("smaller subtle eyes")
    
    if face_opts['eye_distance'] > 30:
        prompt_parts.append("wide-set eyes")
    elif face_opts['eye_distance'] < -30:
        prompt_parts.append("close-set eyes")
    
    # 코
    if face_opts['nose_size'] > 30:
        prompt_parts.append("prominent nose")
    elif face_opts['nose_size'] < -30:
        prompt_parts.append("delicate small nose")
    
    # 입
    if face_opts['mouth_size'] > 30:
        prompt_parts.append("full lips")
    elif face_opts['mouth_size'] < -30:
        prompt_parts.append("thin lips")
    
    # 얼굴형
    if face_opts['face_width'] > 30:
        prompt_parts.append("broad face")
    elif face_opts['face_width'] < -30:
        prompt_parts.append("narrow face")
    
    if face_opts['face_length'] > 30:
        prompt_parts.append("elongated face")
    elif face_opts['face_length'] < -30:
        prompt_parts.append("compact face shape")
    
    # 피부
    if face_opts['skin_smoothness'] > 70:
        prompt_parts.append("flawless smooth skin")
    elif face_opts['skin_smoothness'] < 30:
        prompt_parts.append("textured natural skin")
    
    # 밝기
    if face_opts['brightness'] > 30:
        prompt_parts.append("bright complexion")
    elif face_opts['brightness'] < -30:
        prompt_parts.append("subtle darker tones")
    
    return ", ".join(prompt_parts) if prompt_parts else ""


def lighting_options_to_prompt(lighting_opts):
    """조명 옵션을 프롬프트 텍스트로 변환"""
    # 조명 타입 매핑
    lighting_map = {
        "자연광 (Natural Light)": "natural daylight, soft ambient lighting",
        "스튜디오 조명 (Studio)": "professional studio lighting, controlled environment",
        "소프트박스 (Softbox)": "soft diffused lighting, even illumination",
        "링라이트 (Ring Light)": "ring light setup, circular catchlights in eyes",
        "극적인 조명 (Dramatic)": "dramatic lighting, high contrast",
        "황금빛 (Golden Hour)": "golden hour lighting, warm tones"
    }
    
    # 방향 매핑
    direction_map = {
        "정면 (Frontal)": "frontal lighting",
        "45도 위 (45° High)": "45-degree high-angle lighting",
        "측면 (Side)": "side lighting, emphasizing contours",
        "백라이트 (Backlight)": "backlit, rim lighting effect",
        "상단 (Top)": "top lighting, overhead illumination"
    }
    
    # 강도
    intensity_level = "high" if lighting_opts['lighting_intensity'] > 70 else \
                     "medium" if lighting_opts['lighting_intensity'] > 40 else "low"
    
    # 그림자
    shadow_level = "deep shadows" if lighting_opts['shadow_strength'] > 60 else \
                   "soft shadows" if lighting_opts['shadow_strength'] > 30 else "minimal shadows"
    
    # 대비 및 채도
    adjustments = []
    if lighting_opts['contrast'] > 20:
        adjustments.append("high contrast")
    elif lighting_opts['contrast'] < -20:
        adjustments.append("low contrast")
    
    if lighting_opts['saturation'] > 20:
        adjustments.append("vibrant colors")
    elif lighting_opts['saturation'] < -20:
        adjustments.append("desaturated tones")
    
    # 최종 조합
    parts = [
        lighting_map[lighting_opts['lighting_type']],
        direction_map[lighting_opts['lighting_direction']],
        f"{intensity_level} intensity",
        shadow_level
    ]
    
    if adjustments:
        parts.extend(adjustments)
    
    return ", ".join(parts)


def build_enhanced_prompt(base_prompt, advanced_opts, face_opts, lighting_opts, beauty_opts=None, custom_prompt=""):
    """모든 옵션을 결합하여 최종 프롬프트 생성 (뷰티 보정 포함)"""
    
    # 커스텀 프롬프트가 있으면 우선 사용
    if custom_prompt.strip():
        prompt_parts = [custom_prompt.strip()]
    else:
        prompt_parts = [base_prompt]
    
    # 뷰티 보정 추가 (최우선 - 가장 먼저 적용)
    if beauty_opts:
        beauty_prompt = beauty_options_to_prompt(beauty_opts)
        if beauty_prompt:
            prompt_parts.insert(1 if custom_prompt.strip() else 1, beauty_prompt)
    
    # 얼굴 조정 추가
    face_prompt = face_options_to_prompt(face_opts)
    if face_prompt:
        prompt_parts.append(face_prompt)
    
    # 조명 추가
    lighting_prompt = lighting_options_to_prompt(lighting_opts)
    prompt_parts.append(lighting_prompt)
    
    # 품질 관련
    quality_terms = [
        "high quality",
        "detailed",
        "professional photography",
        "8k resolution" if "4096" in advanced_opts['resolution'] else "4k resolution"
    ]
    prompt_parts.append(", ".join(quality_terms))
    
    # 최종 조합
    final_prompt = ". ".join(prompt_parts) + "."
    
    return final_prompt


def show_detailed_prompt_preview(base_prompt, advanced_opts, face_opts, lighting_opts, beauty_opts=None, custom_prompt=""):
    """
    전체 옵션별 프롬프트를 상세하게 보여주는 함수
    """
    with st.expander("📝 전체 옵션 프롬프트 미리보기 (상세)", expanded=False):
        st.markdown("ℹ️ **각 옵션별로 어떤 프롬프트가 생성되는지 확인하세요**")
        
        # 1. 기본 프롬프트
        st.markdown("---")
        st.markdown("### 1️⃣ 기본 프롬프트 (Base Prompt)")
        if custom_prompt.strip():
            st.code(custom_prompt.strip(), language="text")
            st.markdown("⚠️ 커스텀 프롬프트가 설정되어 기본 옵션들은 무시됩니다.")
        else:
            st.code(base_prompt, language="text")
        
        # 2. 뷰티 보정 프롬프트
        if beauty_opts:
            st.markdown("---")
            st.markdown("### 2️⃣ 뷰티 보정 (Beauty Retouch)")
            beauty_prompt = beauty_options_to_prompt(beauty_opts)
            if beauty_prompt:
                st.code(beauty_prompt, language="text")
                
                # 뷰티 옵션 상세 정보
                with st.expander("💄 뷰티 옵션 상세"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"• **메이크업 타입**: {beauty_opts.get('makeup_type', 'natural')}")
                        st.write(f"• **화이트닝**: {beauty_opts.get('whitening', 0)}")
                        st.write(f"• **피부 매끄러움**: {beauty_opts.get('skin_texture', 0)}")
                    with col2:
                        st.write(f"• **물광 효과**: {beauty_opts.get('glow_effect', 0)}")
                        st.write(f"• **화장 농도**: {beauty_opts.get('makeup_intensity', 0)}")
                        st.write(f"• **보정 부위**: {', '.join(beauty_opts.get('retouch_areas', []))}")
            else:
                st.markdown("⚠️ 뷰티 보정 옵션이 설정되지 않았습니다.")
        
        # 3. 얼굴 조정 프롬프트
        st.markdown("---")
        st.markdown("### 3️⃣ 얼굴 조정 (Face Refinement)")
        face_prompt = face_options_to_prompt(face_opts)
        if face_prompt:
            st.code(face_prompt, language="text")
            with st.expander("👤 얼굴 옵션 상세"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"• **얼굴형**: {face_opts.get('face_shape', '기본')}")
                    st.write(f"• **눈 크기**: {face_opts.get('eye_size', 50)}")
                with col2:
                    st.write(f"• **코 크기**: {face_opts.get('nose_size', 50)}")
                    st.write(f"• **입술 크기**: {face_opts.get('lip_size', 50)}")
        else:
            st.markdown("⚠️ 얼굴 조정 옵션이 설정되지 않았습니다.")
        
        # 4. 조명 설정 프롬프트
        st.markdown("---")
        st.markdown("### 4️⃣ 조명 설정 (Lighting)")
        lighting_prompt = lighting_options_to_prompt(lighting_opts)
        st.code(lighting_prompt, language="text")
        with st.expander("💡 조명 옵션 상세"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"• **조명 타입**: {lighting_opts.get('lighting_type', '자연광')}")
                st.write(f"• **조명 강도**: {lighting_opts.get('lighting_intensity', 0)}")
            with col2:
                st.write(f"• **조명 방향**: {lighting_opts.get('lighting_direction', '정면')}")
                st.write(f"• **그림자 강도**: {lighting_opts.get('shadow_strength', 0)}")
        
        # 5. 품질 설정
        st.markdown("---")
        st.markdown("### 5️⃣ 품질 설정 (Quality)")
        quality_terms = [
            "high quality",
            "detailed",
            "professional photography",
            "8k resolution" if "4096" in advanced_opts['resolution'] else "4k resolution"
        ]
        st.code(", ".join(quality_terms), language="text")
        with st.expander("🌟 고급 옵션 상세"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"• **해상도**: {advanced_opts.get('resolution', '1024x1024')}")
                st.write(f"• **샘플링 단계**: {advanced_opts.get('steps', 50)}")
            with col2:
                st.write(f"• **Seed**: {advanced_opts.get('seed', 'random')}")
                st.write(f"• **프롬프트 강도**: {advanced_opts.get('guidance_scale', 7.5)}")
        
        # 6. 최종 통합 프롬프트
        st.markdown("---")
        st.markdown("### 🎯 최종 통합 프롬프트")
        final_prompt = build_enhanced_prompt(base_prompt, advanced_opts, face_opts, lighting_opts, beauty_opts, custom_prompt)
        st.code(final_prompt, language="text")
        
        # 네거티브 프롬프트
        if advanced_opts.get('negative_prompt'):
            st.markdown("---")
            st.markdown("### 네거티브 프롬프트")
            st.code(advanced_opts['negative_prompt'], language="text")
        
        # 프롬프트 길이 정보
        st.markdown("---")
        st.info(f"📏 **프롬프트 총 길이**: {len(final_prompt)} 문자 | **단어 수**: {len(final_prompt.split())} 개")


def process_replicate_output(output):
    """Replicate API 출력을 URL 리스트로 변환"""
    if isinstance(output, list):
        return output
    elif isinstance(output, str):
        return [output]
    elif hasattr(output, '__iter__'):
        # FileOutput 등의 이터레이터 처리
        urls = []
        for item in output:
            if isinstance(item, str):
                urls.append(item)
            elif hasattr(item, 'url'):
                urls.append(item.url)
        return urls
    else:
        return [str(output)]


# API 키 검증 함수
def verify_google_api_key(api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("test")
        return True
    except Exception as e:
        return False

def verify_replicate_api_key(api_key):
    try:
        os.environ["REPLICATE_API_TOKEN"] = api_key
        replicate.Client(api_token=api_key)
        return True
    except Exception as e:
        return False


# 로그인 페이지
def login_page():
    st.markdown('<div class="main-header"><h1>헤어스타일 모델 생성기</h1><p>AI 제공자를 선택하고 로그인하세요</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        st.markdown("### 🔑 로그인")
        
        # API 제공자 선택
        provider = st.radio(
            "AI 제공자 선택",
            ["Google AI Studio (Gemini)", "Replicate (Seedream 4.0)"],
            help="각 제공자는 다른 기능과 가격을 제공합니다"
        )
        
        st.markdown("")
        
        # Google AI Studio
        if provider == "Google AI Studio (Gemini)":
            st.markdown('<div class="info-box">📌 <b>Google AI Studio</b><br>• 무료 일일 100회<br>• Gemini 2.5 Flash Image<br>• 고품질 이미지 생성</div>', unsafe_allow_html=True)
            
            api_key = st.text_input(
                "Google AI Studio API 키",
                type="password",
                placeholder="AIzaSy...",
                help="https://aistudio.google.com/app/apikey"
            )
            
            if st.button("🔐 Google로 로그인", use_container_width=True):
                if not api_key:
                    st.error("API 키를 입력해주세요")
                else:
                    with st.spinner("API 키 검증 중..."):
                        if verify_google_api_key(api_key):
                            st.session_state.api_key = api_key
                            st.session_state.api_provider = "google"
                            st.session_state.logged_in = True
                            st.success("Google AI Studio 로그인 성공!")
                            st.rerun()
                        else:
                            st.error("유효하지 않은 API 키입니다")
        
        # Replicate
        else:
            st.markdown('<div class="info-box">📌 <b>Replicate (Seedream 4.0)</b><br>• 개인 크레딧 사용<br>• 4K 해상도 지원<br>• 업스케일링 기능<br>• 초고속 생성</div>', unsafe_allow_html=True)
            
            api_key = st.text_input(
                "Replicate API 토큰",
                type="password",
                placeholder="r8_...",
                help="https://replicate.com/account/api-tokens"
            )
            
            if st.button("🔐 Replicate로 로그인", use_container_width=True):
                if not api_key:
                    st.error("API 토큰을 입력해주세요")
                else:
                    with st.spinner("API 토큰 검증 중..."):
                        if verify_replicate_api_key(api_key):
                            st.session_state.api_key = api_key
                            st.session_state.api_provider = "replicate"
                            st.session_state.logged_in = True
                            st.success("Replicate 로그인 성공!")
                            st.rerun()
                        else:
                            st.error("유효하지 않은 API 토큰입니다")
        
        st.markdown("---")
        
        # API 키 발급 안내
        if provider == "Google AI Studio (Gemini)":
            st.info("💡 **Google API 키 발급**\n\n1. https://aistudio.google.com 접속\n2. 'Get API key' 클릭\n3. API 키 생성 및 복사")
        else:
            st.info("💡 **Replicate API 토큰 발급**\n\n1. https://replicate.com 가입\n2. Account → API tokens\n3. 토큰 생성 및 복사")


# Google 메인 선택 화면 (5개 옵션)
def google_main_selection():
    st.markdown('<div class="main-header"><h1>헤어스타일 모델 생성기</h1><span class="provider-badge badge-google">Google Gemini</span></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([4, 1, 1])
    with col3:
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.api_key = None
            st.session_state.api_provider = None
            st.rerun()
    
    st.markdown("## 작업을 선택하세요")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("이미지 생성", key="gen_google", use_container_width=True):
            st.session_state.selected_mode = "generation"
            st.rerun()
        
        if st.button("의상 변경", key="outfit_google", use_container_width=True):
            st.session_state.selected_mode = "outfit"
            st.rerun()
        
        if st.button("얼굴 변경", key="face_google", use_container_width=True):
            st.session_state.selected_mode = "face"
            st.rerun()
    
    with col2:
        if st.button("배경 변경", key="bg_google", use_container_width=True):
            st.session_state.selected_mode = "background"
            st.rerun()
        
        if st.button("헤어 컬러 변경", key="color_google", use_container_width=True):
            st.session_state.selected_mode = "color"
            st.rerun()


# Replicate 메인 선택 화면 (3개 옵션)
def replicate_main_selection():
    st.markdown('<div class="main-header"><h1>헤어스타일 모델 생성기</h1><span class="provider-badge badge-replicate">Replicate Seedream</span></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([4, 1, 1])
    with col3:
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.api_key = None
            st.session_state.api_provider = None
            st.rerun()
    
    st.markdown("## 작업을 선택하세요")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("이미지 생성", key="gen_replicate", use_container_width=True):
            st.session_state.selected_mode = "generation"
            st.rerun()
    
    with col2:
        if st.button("이미지 편집", key="edit_replicate", use_container_width=True):
            st.session_state.selected_mode = "edit_menu"
            st.rerun()
    
    with col3:
        if st.button("업스케일링", key="upscale_replicate", use_container_width=True):
            st.session_state.selected_mode = "upscale"
            st.rerun()


# Replicate 이미지 편집 서브메뉴
def replicate_edit_submenu():
    st.markdown('<div class="main-header"><h1>이미지 편집</h1><span class="provider-badge badge-replicate">Replicate Seedream</span></div>', unsafe_allow_html=True)
    
    if st.button("← 돌아가기"):
        st.session_state.selected_mode = None
        st.rerun()
    
    st.markdown("## 편집 유형을 선택하세요")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("얼굴 변경", key="face_replicate", use_container_width=True):
            st.session_state.selected_mode = "face"
            st.rerun()
        
        if st.button("배경 변경", key="bg_replicate", use_container_width=True):
            st.session_state.selected_mode = "background"
            st.rerun()
    
    with col2:
        if st.button("의상 변경", key="outfit_replicate", use_container_width=True):
            st.session_state.selected_mode = "outfit"
            st.rerun()
        
        if st.button("헤어 컬러 변경", key="color_replicate", use_container_width=True):
            st.session_state.selected_mode = "color"
            st.rerun()


# 이미지 생성 페이지 (Google) - 참조 이미지 + 커스텀 프롬프트 추가
def generation_page_google():
    st.markdown('<div class="main-header"><h1>이미지 생성</h1><span class="provider-badge badge-google">Google Gemini</span></div>', unsafe_allow_html=True)
    
    if st.button("⬅️ 뒤로 가기"):
        st.session_state.selected_mode = None
        st.rerun()
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 모델 정보")
        
        age_group = st.selectbox("나이대", ["10대", "20대", "30대", "40대", "50대"])
        gender = st.selectbox("성별", ["여성", "남성"])
        skin_tone = st.selectbox("피부톤", ["밝은 톤", "보통 톤", "어두운 톤"])
        
        st.markdown("### 💇 헤어스타일")
        
        if gender == "여성":
            hair_length = st.selectbox("기장", [
                "숏컷 (pixie cut)",
                "숏단발 (short bob)",
                "중간머리 (shoulder length)",
                "단발머리 (long bob)",
                "긴머리 (long hair)"
            ])
        else:
            hair_length = st.selectbox("스타일", [
                "내린머리 (down-styled)",
                "올린머리 (up-styled)",
                "투블럭 (undercut)"
            ])
        
        hair_texture = st.selectbox("헤어 질감", ["스트레이트", "C컬", "웨이브"])
        hair_color = st.selectbox("헤어 컬러", [
            "자연흑발",
            "다크 브라운",
            "브라운",
            "애쉬 브라운",
            "밝은 브라운"
        ])
        hair_volume = st.selectbox("볼륨감", ["볼륨있는", "자연스러운", "얇은/가벼운"])
        bangs = st.selectbox("앞머리", ["있음", "없음", "시스루뱅"])
        
        st.markdown("### 📸 촬영 설정")
        
        shot_type = st.selectbox("샷 타입", ["헤드샷 (headshot)", "상반신 (upper body)"])
        angle = st.selectbox("앵글", ["정면 (front view)", "45도 (3/4 view)", "측면 (side profile)"])
        expression = st.selectbox("표정", ["무표정", "은은한 미소", "자연스러운 미소"])
        lighting = st.selectbox("조명", ["스튜디오 조명", "자연광", "소프트 라이팅"])
        background = st.selectbox("배경", [
            "흰색 무지 배경",
            "회색 무지 배경",
            "스튜디오 배경",
            "블러 처리된 실내"
        ])
        
        # 참조 이미지 업로드 추가
        st.markdown("---")
        st.markdown("### 🖼️ 참조 이미지 (선택사항)")
        st.markdown("💡 스타일 참조용 이미지를 업로드하면 더 정확한 결과를 얻을 수 있습니다 (최대 3개)")
        
        ref_image1 = st.file_uploader("참조 이미지 1", type=['png', 'jpg', 'jpeg'], key="ref1_gen")
        ref_image2 = st.file_uploader("참조 이미지 2", type=['png', 'jpg', 'jpeg'], key="ref2_gen")
        ref_image3 = st.file_uploader("참조 이미지 3", type=['png', 'jpg', 'jpeg'], key="ref3_gen")
        
        ref_cols = st.columns(3)
        with ref_cols[0]:
            if ref_image1:
                st.image(ref_image1, caption="참조 1", use_container_width=True)
        with ref_cols[1]:
            if ref_image2:
                st.image(ref_image2, caption="참조 2", use_container_width=True)
        with ref_cols[2]:
            if ref_image3:
                st.image(ref_image3, caption="참조 3", use_container_width=True)
        
        # 커스텀 프롬프트 입력 추가
        st.markdown("---")
        st.markdown("### ✍️ 커스텀 프롬프트 (선택사항)")
        custom_prompt = st.text_area(
            "원하는 스타일을 자유롭게 입력하세요",
            placeholder="예: A professional portrait of a Korean woman in her 20s with long wavy hair, wearing a white blouse, studio lighting...",
            height=100,
            help="이 입력란을 사용하면 위의 옵션들은 무시되고 입력한 프롬프트가 사용됩니다"
        )
        
        # 고급 옵션 추가
        st.markdown("---")
        advanced_opts = render_advanced_options()
        face_opts = render_face_refinement()
        beauty_opts = render_beauty_retouch()
        lighting_opts = render_lighting_options()
    
    with col2:
        st.markdown("### 🎨 생성 결과")
        
        if st.button("이미지 생성", use_container_width=True):
            with st.spinner("이미지 생성 중... 약 30초 소요됩니다"):
                try:
                    # 프롬프트 생성
                    if not custom_prompt.strip():
                        # 기본 옵션으로 프롬프트 생성
                        age_map = {"10대": "teenage", "20대": "20s", "30대": "30s", "40대": "40s", "50대": "50s"}
                        gender_map = {"여성": "female", "남성": "male"}
                        skin_map = {"밝은 톤": "fair skin", "보통 톤": "medium skin tone", "어두운 톤": "tan skin"}
                        texture_map = {"스트레이트": "straight", "C컬": "soft C-curl", "웨이브": "wavy"}
                        color_map = {
                            "자연흑발": "natural black",
                            "다크 브라운": "dark brown",
                            "브라운": "brown",
                            "애쉬 브라운": "ash brown",
                            "밝은 브라운": "light brown"
                        }
                        volume_map = {"볼륨있는": "voluminous", "자연스러운": "natural", "얇은/가벼운": "flat"}
                        bangs_map = {"있음": "with bangs", "없음": "no bangs", "시스루뱅": "with see-through bangs"}
                        
                        base_prompt = f"""
A professional studio portrait photograph of a Korean {age_map[age_group]} {gender_map[gender]}.

COMPOSITION:
- Shot type: {shot_type}
- Angle: {angle}
- Expression: {expression}

HAIR (PRIMARY FOCUS):
- Style: {hair_length} {texture_map[hair_texture]} hair
- Color: {color_map[hair_color]}
- Volume: {volume_map[hair_volume]} volume
- Bangs: {bangs_map[bangs]}

SUBJECT DETAILS:
- Skin tone: {skin_map[skin_tone]}
- Clean, professional appearance

TECHNICAL SETTINGS:
- Lighting: {lighting} creating even, flattering illumination
- Background: {background}
- Image quality: High-resolution, sharp focus on hair details
- Aspect ratio: Portrait orientation

The final image should showcase the hairstyle clearly with professional salon-quality photography standards.
"""
                    else:
                        base_prompt = custom_prompt
                    
                    # 고급 옵션 적용
                    final_prompt = build_enhanced_prompt(base_prompt, advanced_opts, face_opts, lighting_opts, beauty_opts, custom_prompt)
                    
                    # 네거티브 프롬프트 추가
                    if advanced_opts['negative_prompt']:
                        final_prompt += f"\n\nNegative prompt: {advanced_opts['negative_prompt']}"
                    
                    # 상세 프롬프트 미리보기
                    show_detailed_prompt_preview(base_prompt, advanced_opts, face_opts, lighting_opts, beauty_opts, custom_prompt)
                    
                    # 참조 이미지 준비
                    content_list = [final_prompt]
                    if ref_image1:
                        content_list.append(Image.open(ref_image1))
                    if ref_image2:
                        content_list.append(Image.open(ref_image2))
                    if ref_image3:
                        content_list.append(Image.open(ref_image3))
                    
                    # API 호출
                    genai.configure(api_key=st.session_state.api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash-image')
                    response = model.generate_content(content_list)
                    
                    # 결과 표시
                    for part in response.candidates[0].content.parts:
                        if part.inline_data is not None:
                            image_data = part.inline_data.data
                            image = Image.open(io.BytesIO(image_data))
                            
                            st.image(image, use_container_width=True)
                            
                            # 다운로드 버튼
                            buf = io.BytesIO()
                            image.save(buf, format="PNG")
                            st.download_button(
                                label="💾 이미지 다운로드",
                                data=buf.getvalue(),
                                file_name=f"hairstyle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                mime="image/png",
                                use_container_width=True
                            )
                            
                            st.success("이미지 생성 완료!")
                
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")


# 이미지 생성 페이지 (Replicate) - 참조 이미지 + 커스텀 프롬프트 추가
def generation_page_replicate():
    st.markdown('<div class="main-header"><h1>이미지 생성</h1><span class="provider-badge badge-replicate">Replicate Seedream</span></div>', unsafe_allow_html=True)
    
    if st.button("⬅️ 뒤로 가기"):
        st.session_state.selected_mode = None
        st.rerun()
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 모델 정보")
        
        age_group = st.selectbox("나이대", ["10대", "20대", "30대", "40대", "50대"])
        gender = st.selectbox("성별", ["여성", "남성"])
        skin_tone = st.selectbox("피부톤", ["밝은 톤", "보통 톤", "어두운 톤"])
        
        st.markdown("### 💇 헤어스타일")
        
        if gender == "여성":
            hair_length = st.selectbox("기장", [
                "숏컷 (pixie cut)",
                "숏단발 (short bob)",
                "중간머리 (shoulder length)",
                "단발머리 (long bob)",
                "긴머리 (long hair)"
            ])
        else:
            hair_length = st.selectbox("스타일", [
                "내린머리 (down-styled)",
                "올린머리 (up-styled)",
                "투블럭 (undercut)"
            ])
        
        hair_texture = st.selectbox("헤어 질감", ["스트레이트", "C컬", "웨이브"])
        hair_color = st.selectbox("헤어 컬러", [
            "자연흑발",
            "다크 브라운",
            "브라운",
            "애쉬 브라운",
            "밝은 브라운"
        ])
        hair_volume = st.selectbox("볼륨감", ["볼륨있는", "자연스러운", "얇은/가벼운"])
        bangs = st.selectbox("앞머리", ["있음", "없음", "시스루뱅"])
        
        st.markdown("### 📸 촬영 설정")
        
        shot_type = st.selectbox("샷 타입", ["헤드샷 (headshot)", "상반신 (upper body)"])
        angle = st.selectbox("앵글", ["정면 (front view)", "45도 (3/4 view)", "측면 (side profile)"])
        expression = st.selectbox("표정", ["무표정", "은은한 미소", "자연스러운 미소"])
        lighting = st.selectbox("조명", ["스튜디오 조명", "자연광", "소프트 라이팅"])
        background = st.selectbox("배경", [
            "흰색 무지 배경",
            "회색 무지 배경",
            "스튜디오 배경",
            "블러 처리된 실내"
        ])
        
        # 참조 이미지 업로드 추가
        st.markdown("---")
        st.markdown("### 🖼️ 참조 이미지 (선택사항)")
        st.markdown("💡 스타일 참조용 이미지를 업로드하면 Image-to-Image 모드로 작동합니다")
        
        ref_image = st.file_uploader("참조 이미지", type=['png', 'jpg', 'jpeg'], key="ref_replicate_gen")
        
        if ref_image:
            st.image(ref_image, caption="참조 이미지", use_container_width=True)
        
        # 커스텀 프롬프트 입력 추가
        st.markdown("---")
        st.markdown("### ✍️ 커스텀 프롬프트 (선택사항)")
        custom_prompt = st.text_area(
            "원하는 스타일을 자유롭게 입력하세요",
            placeholder="예: A professional portrait of a Korean woman in her 20s with long wavy hair, wearing a white blouse, studio lighting...",
            height=100,
            help="이 입력란을 사용하면 위의 옵션들은 무시되고 입력한 프롬프트가 사용됩니다"
        )
        
        # 고급 옵션 추가
        st.markdown("---")
        advanced_opts = render_advanced_options()
        face_opts = render_face_refinement()
        beauty_opts = render_beauty_retouch()
        lighting_opts = render_lighting_options()
    
    with col2:
        st.markdown("### 🎨 생성 결과")
        
        num_images = advanced_opts['num_images']
        
        if st.button("이미지 생성", use_container_width=True):
            with st.spinner(f"이미지 생성 중... {num_images}개 생성 예상 시간: 약 {num_images * 10}초"):
                try:
                    # 프롬프트 생성
                    if not custom_prompt.strip():
                        age_map = {"10대": "teenage", "20대": "20s", "30대": "30s", "40대": "40s", "50대": "50s"}
                        gender_map = {"여성": "female", "남성": "male"}
                        skin_map = {"밝은 톤": "fair skin", "보통 톤": "medium skin tone", "어두운 톤": "tan skin"}
                        texture_map = {"스트레이트": "straight", "C컬": "soft C-curl", "웨이브": "wavy"}
                        color_map = {
                            "자연흑발": "natural black",
                            "다크 브라운": "dark brown",
                            "브라운": "brown",
                            "애쉬 브라운": "ash brown",
                            "밝은 브라운": "light brown"
                        }
                        volume_map = {"볼륨있는": "voluminous", "자연스러운": "natural", "얇은/가벼운": "flat"}
                        bangs_map = {"있음": "with bangs", "없음": "no bangs", "시스루뱅": "with see-through bangs"}
                        
                        base_prompt = f"""
A professional studio portrait photograph of a Korean {age_map[age_group]} {gender_map[gender]}.

COMPOSITION:
- Shot type: {shot_type}
- Angle: {angle}
- Expression: {expression}

HAIR (PRIMARY FOCUS):
- Style: {hair_length} {texture_map[hair_texture]} hair
- Color: {color_map[hair_color]}
- Volume: {volume_map[hair_volume]} volume
- Bangs: {bangs_map[bangs]}

SUBJECT DETAILS:
- Skin tone: {skin_map[skin_tone]}
- Clean, professional appearance

TECHNICAL SETTINGS:
- Lighting: {lighting} creating even, flattering illumination
- Background: {background}
- Image quality: High-resolution, sharp focus on hair details
- Aspect ratio: Portrait orientation

The final image should showcase the hairstyle clearly with professional salon-quality photography standards.
"""
                    else:
                        base_prompt = custom_prompt
                    
                    # 고급 옵션 적용
                    final_prompt = build_enhanced_prompt(base_prompt, advanced_opts, face_opts, lighting_opts, beauty_opts, custom_prompt)
                    
                    # 상세 프롬프트 미리보기
                    show_detailed_prompt_preview(base_prompt, advanced_opts, face_opts, lighting_opts, beauty_opts, custom_prompt)
                    
                    # Replicate API 호출
                    os.environ["REPLICATE_API_TOKEN"] = st.session_state.api_key
                    
                    # 참조 이미지가 있으면 Image-to-Image 모드
                    input_params = {
                        "prompt": final_prompt,
                        "num_outputs": num_images,
                        "seed": advanced_opts['seed'],
                        "guidance_scale": advanced_opts['guidance_scale'],
                        "num_inference_steps": advanced_opts['steps'],
                        "negative_prompt": advanced_opts['negative_prompt'],
                        "aspect_ratio": "1:1",
                        "output_format": "png"
                    }
                    
                    if ref_image:
                        # 이미지를 base64로 변환
                        image = Image.open(ref_image)
                        buffered = io.BytesIO()
                        image.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        data_uri = f"data:image/png;base64,{img_str}"
                        input_params["image"] = data_uri
                        input_params["prompt_strength"] = 0.8
                    
                    output = replicate.run(
                        "bytedance/seedream-4",
                        input=input_params
                    )
                    
                    # 결과 처리
                    image_urls = process_replicate_output(output)
                    
                    for idx, image_url in enumerate(image_urls):
                        st.image(image_url, caption=f"생성 이미지 {idx + 1}", use_container_width=True)
                        st.markdown(f"[💾 이미지 {idx + 1} 다운로드]({image_url})")
                    
                    st.success(f"✅ {len(image_urls)}개 이미지 생성 완료!")
                
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")


# 업스케일링 페이지 (Replicate 전용) - 커스텀 프롬프트 추가
def upscale_page_replicate():
    st.markdown('<div class="main-header"><h1>업스케일링</h1><span class="provider-badge badge-replicate">Replicate Seedream</span></div>', unsafe_allow_html=True)
    
    if st.button("⬅️ 뒤로 가기"):
        st.session_state.selected_mode = None
        st.rerun()
    
    st.markdown('<div class="info-box">💡 <b>업스케일링 기능</b><br>저해상도 이미지를 4K까지 업스케일하여 선명도를 높입니다.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 이미지 업로드")
        
        input_image = st.file_uploader("업스케일할 이미지", type=['png', 'jpg', 'jpeg'], key="upscale_input")
        
        if input_image:
            st.image(input_image, caption="원본 이미지", use_container_width=True)
            
            st.markdown("### ⚙️ 업스케일 설정")
            scale_factor = st.selectbox("배율", ["2x", "4x"], index=1)
            
            # 커스텀 프롬프트 입력 추가
            st.markdown("---")
            st.markdown("### ✍️ 추가 프롬프트 (선택사항)")
            custom_prompt = st.text_area(
                "업스케일 시 강조할 요소를 입력하세요",
                placeholder="예: sharp details, clear hair texture, professional quality...",
                height=80,
                help="추가 프롬프트를 입력하면 업스케일 품질이 향상될 수 있습니다"
            )
            
            # 고급 옵션 추가
            st.markdown("---")
            advanced_opts = render_advanced_options()
    
    with col2:
        st.markdown("### 🎨 업스케일 결과")
        
        if st.button("✨ 업스케일링 시작", use_container_width=True):
            if not input_image:
                st.error("이미지를 업로드해주세요!")
            else:
                with st.spinner("업스케일 중... 약 20-30초 소요됩니다"):
                    try:
                        # 이미지를 base64로 변환
                        image = Image.open(input_image)
                        buffered = io.BytesIO()
                        image.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        data_uri = f"data:image/png;base64,{img_str}"
                        
                        # Replicate API 호출
                        os.environ["REPLICATE_API_TOKEN"] = st.session_state.api_key
                        
                        st.info("ℹ️ Seedream 4.0의 고해상도 재생성 기능을 사용합니다")
                        
                        # 프롬프트 생성
                        if custom_prompt.strip():
                            upscale_prompt = f"high quality, ultra detailed, {advanced_opts['resolution']} resolution, {custom_prompt}"
                        else:
                            upscale_prompt = f"high quality, ultra detailed, {advanced_opts['resolution']} resolution, sharp details"
                        
                        output = replicate.run(
                            "bytedance/seedream-4",
                            input={
                                "prompt": upscale_prompt,
                                "image": data_uri,
                                "prompt_strength": 0.3,  # 원본 유지
                                "seed": advanced_opts['seed'],
                                "guidance_scale": advanced_opts['guidance_scale'],
                                "num_inference_steps": advanced_opts['steps'],
                                "negative_prompt": advanced_opts['negative_prompt'],
                                "output_format": "png"
                            }
                        )
                        
                        # 결과 표시
                        image_urls = process_replicate_output(output)
                        
                        for idx, url in enumerate(image_urls):
                            st.image(url, use_container_width=True)
                            st.markdown(f"[💾 업스케일 이미지 다운로드]({url})")
                        
                        st.success("업스케일 완료!")
                    
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {str(e)}")
                        st.info("💡 Seedream 4.0의 업스케일 기능은 이미지 편집 모드를 사용합니다")


# 이미지 편집 페이지 (공통) - 커스텀 프롬프트 추가
def edit_page(mode):
    mode_names = {
        "outfit": "의상 변경",
        "face": "얼굴 변경",
        "background": "배경 변경",
        "color": "헤어 컬러 변경"
    }
    
    mode_emojis = {
        "outfit": "👔",
        "face": "👤",
        "background": "🏞️",
        "color": "🎨"
    }
    
    provider_badge = "badge-google" if st.session_state.api_provider == "google" else "badge-replicate"
    provider_name = "Google Gemini" if st.session_state.api_provider == "google" else "Replicate Seedream"
    
    st.markdown(f'<div class="main-header"><h1>{mode_emojis[mode]} {mode_names[mode]}</h1><span class="provider-badge {provider_badge}">{provider_name}</span></div>', unsafe_allow_html=True)
    
    if st.button("⬅️ 뒤로 가기"):
        if st.session_state.api_provider == "replicate":
            st.session_state.selected_mode = "edit_menu"
        else:
            st.session_state.selected_mode = None
        st.rerun()
    
    st.markdown('<div class="warning-box">⚠️ <b>주의:</b> 헤어스타일은 메인 이미지 그대로 유지됩니다</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 이미지 업로드")
        
        main_image = st.file_uploader("메인 이미지 (헤어스타일 유지)", type=['png', 'jpg', 'jpeg'], key=f"main_{mode}")
        
        st.markdown("**샘플 이미지 (1-3개)**")
        st.markdown("💡 팁: 샘플 이미지를 2-3개 업로드하면 더 정확한 결과를 얻을 수 있습니다!")
        
        sample1 = st.file_uploader("샘플 1 (필수)", type=['png', 'jpg', 'jpeg'], key=f"sample1_{mode}")
        sample2 = st.file_uploader("샘플 2 (선택)", type=['png', 'jpg', 'jpeg'], key=f"sample2_{mode}")
        sample3 = st.file_uploader("샘플 3 (선택)", type=['png', 'jpg', 'jpeg'], key=f"sample3_{mode}")
        
        if main_image:
            st.image(main_image, caption="메인 이미지", use_container_width=True)
        
        samples_col1, samples_col2, samples_col3 = st.columns(3)
        with samples_col1:
            if sample1:
                st.image(sample1, caption="샘플 1", use_container_width=True)
        with samples_col2:
            if sample2:
                st.image(sample2, caption="샘플 2", use_container_width=True)
        with samples_col3:
            if sample3:
                st.image(sample3, caption="샘플 3", use_container_width=True)
        
        # 커스텀 프롬프트 입력 추가
        st.markdown("---")
        st.markdown("### ✍️ 커스텀 프롬프트 (선택사항)")
        custom_prompt = st.text_area(
            f"{mode_names[mode]} 시 원하는 스타일을 입력하세요",
            placeholder=f"예: {mode}에 대한 구체적인 설명...",
            height=100,
            help="커스텀 프롬프트를 사용하면 기본 프롬프트 대신 입력한 내용이 사용됩니다"
        )
        
        # 고급 옵션 추가
        st.markdown("---")
        advanced_opts = render_advanced_options()
        face_opts = render_face_refinement()
        beauty_opts = render_beauty_retouch()
        lighting_opts = render_lighting_options()
    
    with col2:
        st.markdown("### 🎨 변경 결과")
        
        if st.button(f"✨ {mode_names[mode]}하기", use_container_width=True):
            if not main_image or not sample1:
                st.error("메인 이미지와 샘플 1은 필수입니다!")
            else:
                with st.spinner("이미지 변경 중... 약 30-60초 소요됩니다"):
                    try:
                        # 프롬프트 선택
                        if not custom_prompt.strip():
                            prompts = {
                                "outfit": """
Create a new image using:
- The person and hairstyle from the FIRST image (main image)
- The outfit style from the remaining sample images

CRITICAL RULES:
1. Keep the hairstyle EXACTLY as shown in the first image:
   - Hair length, hair texture, hair color, hair volume
   - Hair cut, bangs style, hair direction
   - DO NOT change ANY aspect of the hair
2. Apply the outfit style from the sample images
3. Maintain the person's pose and facial features from the first image
4. Keep natural lighting and professional portrait quality

The result should look like the same person from the first image 
wearing the outfit from the sample images.
""",
                                "face": """
Create a new image by combining:
- The hairstyle and outfit from the FIRST image (main image)
- The facial features from the remaining sample images

CRITICAL RULES:
1. Keep the hairstyle from the first image EXACTLY the same:
   - Hair length, texture, color, volume, cut, style
   - DO NOT modify the hair in any way
2. Replace only the facial features (eyes, nose, mouth, face shape)
3. Keep the outfit and pose from the first image
4. Maintain professional portrait quality and natural lighting

The result should have the face from the sample images 
with the exact hairstyle from the first image.
""",
                                "background": """
Create a new image by:
- Keeping the person EXACTLY as shown in the FIRST image (main image)
- Replacing the background with the style from the remaining sample images

CRITICAL RULES:
1. Keep the person completely unchanged:
   - Hairstyle, hair color, face, outfit, pose
   - DO NOT modify ANY aspect of the subject
2. Only change the background/environment
3. Ensure lighting on the person matches the new background naturally
4. Maintain professional portrait quality

The result should be the exact same person in a different environment.
""",
                                "color": """
Create a new image by:
- Using the person from the FIRST image (main image)
- Applying the hair color from the remaining sample images

CRITICAL RULES:
1. ONLY change the hair color - nothing else
2. Keep EXACTLY the same:
   - Hair length, texture, volume, cut, style
   - Bangs style, hair direction, hair flow
   - Face, outfit, background, pose
3. Apply the color naturally with proper highlights and shadows
4. Maintain professional portrait quality

The result should be the exact same hairstyle in a different color.
"""
                            }
                            base_prompt = prompts[mode]
                        else:
                            base_prompt = custom_prompt
                        
                        # 고급 옵션 적용
                        final_prompt = build_enhanced_prompt(base_prompt, advanced_opts, face_opts, lighting_opts, beauty_opts, custom_prompt)
                        
                        # 상세 프롬프트 미리보기
                        show_detailed_prompt_preview(base_prompt, advanced_opts, face_opts, lighting_opts, beauty_opts, custom_prompt)
                        
                        # API별 처리
                        if st.session_state.api_provider == "google":
                            # Google Gemini API
                            main_img = Image.open(main_image)
                            sample1_img = Image.open(sample1)
                            
                            images = [main_img, sample1_img]
                            
                            if sample2:
                                images.append(Image.open(sample2))
                            if sample3:
                                images.append(Image.open(sample3))
                            
                            genai.configure(api_key=st.session_state.api_key)
                            model = genai.GenerativeModel('gemini-2.5-flash-image')
                            
                            response = model.generate_content([final_prompt] + images)
                            
                            for part in response.candidates[0].content.parts:
                                if part.inline_data is not None:
                                    image_data = part.inline_data.data
                                    result_image = Image.open(io.BytesIO(image_data))
                                    
                                    # Before/After 비교 기능
                                    st.markdown("---")
                                    st.markdown("🔄 **Before / After 비교**")
                                    
                                    compare_cols = st.columns(2)
                                    with compare_cols[0]:
                                        st.markdown("**Before (원본)**")
                                        st.image(main_img, use_container_width=True)
                                    with compare_cols[1]:
                                        st.markdown("**After (결과)**")
                                        st.image(result_image, use_container_width=True)
                                    
                                    st.markdown("---")
                                    
                                    buf = io.BytesIO()
                                    result_image.save(buf, format="PNG")
                                    st.download_button(
                                        label="💾 이미지 다운로드",
                                        data=buf.getvalue(),
                                        file_name=f"{mode}_changed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                        mime="image/png",
                                        use_container_width=True
                                    )
                        
                        else:
                            # Replicate Seedream API
                            os.environ["REPLICATE_API_TOKEN"] = st.session_state.api_key
                            
                            # 이미지를 base64로 변환
                            def image_to_data_uri(img_file):
                                image = Image.open(img_file)
                                buffered = io.BytesIO()
                                image.save(buffered, format="PNG")
                                img_str = base64.b64encode(buffered.getvalue()).decode()
                                return f"data:image/png;base64,{img_str}"
                            
                            main_uri = image_to_data_uri(main_image)
                            
                            # Seedream은 단일 참조 이미지 사용
                            output = replicate.run(
                                "bytedance/seedream-4",
                                input={
                                    "prompt": final_prompt,
                                    "image": main_uri,
                                    "prompt_strength": 0.8,
                                    "seed": advanced_opts['seed'],
                                    "guidance_scale": advanced_opts['guidance_scale'],
                                    "num_inference_steps": advanced_opts['steps'],
                                    "negative_prompt": advanced_opts['negative_prompt'],
                                    "output_format": "png"
                                }
                            )
                            
                            image_urls = process_replicate_output(output)
                            
                            for idx, url in enumerate(image_urls):
                                st.image(url, use_container_width=True)
                                st.markdown(f"[💾 이미지 다운로드]({url})")
                        
                        st.success(f"✅ {mode_names[mode]} 완료!")
                    
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {str(e)}")


# 메인 앱 로직
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        if 'selected_mode' not in st.session_state:
            st.session_state.selected_mode = None
        
        # Google AI Studio 로그인
        if st.session_state.api_provider == "google":
            if st.session_state.selected_mode is None:
                google_main_selection()
            elif st.session_state.selected_mode == "generation":
                generation_page_google()
            elif st.session_state.selected_mode in ["outfit", "face", "background", "color"]:
                edit_page(st.session_state.selected_mode)
        
        # Replicate 로그인
        elif st.session_state.api_provider == "replicate":
            if st.session_state.selected_mode is None:
                replicate_main_selection()
            elif st.session_state.selected_mode == "generation":
                generation_page_replicate()
            elif st.session_state.selected_mode == "edit_menu":
                replicate_edit_submenu()
            elif st.session_state.selected_mode == "upscale":
                upscale_page_replicate()
            elif st.session_state.selected_mode in ["outfit", "face", "background", "color"]:
                edit_page(st.session_state.selected_mode)

if __name__ == "__main__":
    main()
