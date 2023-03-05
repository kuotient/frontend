import streamlit as st
import io
import base64
import random
import requests
import streamlit_nested_layout
from streamlit_image_select import image_select
import streamlit_analytics
import os
import time

from PIL import Image
from rembg import remove

# st.set_page_config(page_title="Text-to-Emoji", layout="wide", page_icon="😊")
st.set_page_config(page_title="Text-to-Emoji",
                layout="wide",
                page_icon="🔮",
                menu_items={
        'Get help': 'https://github.com/boostcampaitech4lv23nlp2/final-project-level2-nlp-11/issues',
        'About': 'https://github.com/boostcampaitech4lv23nlp2/final-project-level2-nlp-11'
        })

def main():
    # left, right = st.columns([4, 1])
    st.image("g_logo.png")
    with streamlit_analytics.track():
        with st.sidebar:
            st.title("🔮 Text-to-Emoji")
            st.caption("프롬프트를 입력해 Emoji를 생성해보세요!")
            st.markdown("Made by [*WE-FUSION*](https://github.com/boostcampaitech4lv23nlp2/final-project-level2-nlp-11)")
            st.header("🔧 Settings")
        if "submit" not in st.session_state:
            st.session_state["submit"] = False
        if "prompt" not in st.session_state:
            st.session_state["prompt"] = ""
        if "image_list" not in st.session_state:
            st.session_state["image_list"] = []
        if "output_size" not in st.session_state:
            st.session_state["output_size"] = 256
        if "num_inference" not in st.session_state:
            st.session_state["num_inference"] = None
        if "guidance_scale" not in st.session_state : 
            st.session_state['guidance_scale'] = None
        if "inference_step" not in st.session_state : 
            st.session_state['inference_step'] = None
        if "save_prameter" not in st.session_state : 
            st.session_state['save_prameter'] = {}
        if "model_select" not in st.session_state :
            st.session_state['model_select'] = ""
        if "remove_bg" not in st.session_state :
            st.session_state['remove_bg'] = False
        if "image_style" not in st.session_state :
            st.session_state['image_style'] = ""
        
        with st.sidebar:
            model_select = st.radio(
                "프롬프트 언어 선택",
                ("English",
                "한국어",),
                help="프롬프트에 쓸 언어를 선택할 수 있습니다. 영어 입력 선택 시 성능이 좀 더 좋은 경향이 있습니다."
            )
            # st.sidebar.markdown("이모지 스타일")
            image_style = st.selectbox(
                "Emoji 스타일",
                ("notoemoji","openmoji"),
                help="특정 스타일의 이모지를 생성할 수 있습니다. notoemoji는 구글에서 제공하는 이모지이며, openmoji는 오픈소스로 제공되는 이모지입니다."
            )
        
        st.session_state['image_style'] = image_style
        noto_html = """
                    <div style="display:flex;flex-direction:row;">
                        <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f422/512.gif" width="50" height="50">
                        <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f60e/512.gif" width="50" height="50">
                        <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f48e/512.gif" width="50" height="50">
                        <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f47b/512.gif" width="50" height="50">
                        <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f917/512.gif" width="50" height="50">
                        <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f496/512.gif" width="50" height="50">
                    </div>
                    """
        openmoji_html = """
                        <div style="display:flex;flex-direction:row;">
                            <img src="https://openmoji.org/data/color/svg/1F422.svg" width="50" height="50">
                            <img src="https://openmoji.org/data/color/svg/1F60E.svg" width="50" height="50">
                            <img src="https://openmoji.org/data/color/svg/1F48E.svg" width="50" height="50">
                            <img src="https://openmoji.org/data/color/svg/1F47B.svg" width="50" height="50">
                            <img src="https://openmoji.org/data/color/svg/1F917.svg" width="50" height="50">
                            <img src="https://openmoji.org/data/color/svg/1F496.svg" width="50" height="50">
                        </div>
                        """

        if st.session_state.image_style == "openmoji":
            st.sidebar.markdown(openmoji_html, unsafe_allow_html=True)
        else:
            st.sidebar.markdown(noto_html, unsafe_allow_html=True)
        
        # st.sidebar.markdown("이모지 아웃풋 크기")
        output_option = st.sidebar.selectbox(
            "Emoji 출력 크기",
            ("512","256","128"),
            help = "이모지의 출력 크기를 선택할 수 있습니다."
        )

        # st.sidebar.markdown("Number of outputs")
        with st.sidebar:
            num_inference = st.slider("생성 할 emoji 갯수",1,4,2,help="생성할 emoji의 갯수를 선택할 수 있습니다. 1~4개까지 선택 가능합니다.")
        st.session_state['num_inference'] = int(num_inference)
        
        if st.session_state.num_inference == 1:
            st.sidebar.info("  예상 소요 시간: 5~6초", icon="ℹ️")
        elif st.session_state.num_inference == 2:
            st.sidebar.info("  예상 소요 시간: 10~12초", icon="ℹ️")
        elif st.session_state.num_inference == 3:
            st.sidebar.warning("  예상 소요 시간: 16~20초", icon="⚠️")
        else:
            st.sidebar.error("  예상 소요 시간: 20~25초", icon="🚨")

        # st.sidebar.markdown("cfg scale")
        with st.sidebar:
            guidance_scale = st.slider("Cfg scale",0, 25, 10,help="Emoji가 prompt를 따라가는 정도를 조절할 수 있습니다. 0~25까지 선택 가능합니다.")
        st.session_state['guidance_scale'] = int(guidance_scale)
        
        if st.session_state['guidance_scale'] >= 15:
            st.sidebar.warning("과도한 cfg scale 파라미터는 이미지 품질의 저하를 일으킬 수 있습니다.", icon="⚠️")
        else:
            st.empty()


        st.session_state['model_select'] = model_select
        st.session_state['output_size'] = int(output_option)
        st.session_state['inference_step'] = 30
        
        
            # st.markdown("## Text-to-Emoji")

            # with st.form(key="my_form", clear_on_submit=True):
                # col1, col2 = st.columns([8, 2])

                # with col1:
                #     st.text_input(
                #         label= "Input Text(Prompt)",
                #         placeholder = "A cute rabbit",
                #         value = st.session_state.prompt,
                #         key="prompt",
                #         label_visibility="collapsed",
                #     )
                # with col2:
                #     submit = st.form_submit_button(label="submit")
                #     if submit:
                #         st.session_state.submit = True
        st.warning("Deprecated. 전체 프로젝트는 Github을 참고해주세요. https://github.com/boostcampaitech4lv23nlp2/final-project-level2-nlp-11")
        st.text_input(
            label= " ",
            placeholder = "Hot air balloon floating peacefully above rolling countryside dotted with farms and fields." if st.session_state.model_select== "English" else "귀여운 토끼",
            value = st.session_state.prompt,
            key="prompt",
            max_chars=75,
            help="프롬프트를 입력해주세요. 최대 75자까지 입력 가능합니다."
            # label_visibility="collapsed",
        )
        # co3, col1, col2, col4 = st.columns([2,1,1,2])
        col1, col2, col0, col3 = st.columns([1,1,1,2])
        with col1:
            generate = st.button(label="Emoji 생성", type="primary", help="Emoji를 생성합니다. 시간이 조금 걸릴 수 있습니다.")
            if generate:
                if not st.session_state.prompt:
                    st.warning("프롬프트를 입력해주세요.")
                elif st.session_state.prompt:
                    st.session_state.submit = True
                else:
                    st.error("Something is wrong.")
            
        with col2:
            feeling_lucky = st.button(label="I'm Feeling Lucky", type="secondary", help="무작위 프롬프트를 이용해 Emoji를 생성합니다.")
                
            if feeling_lucky:
                if st.session_state.model_select == "English":
                    lang_prompt = "prompt.txt"
                else:
                    lang_prompt = "kor_prompt.txt"
                    
                with open(lang_prompt) as f:
                    sample_prompts = f.read().splitlines()
                lucky_prompt = random.choice(sample_prompts)
                # print(lucky_prompt)
                st.session_state.submit = True
        col0.empty()
        if st.session_state.submit:
            if feeling_lucky:
                data = {
                    "prompt": lucky_prompt,
                    "model": st.session_state.image_style,
                    "guidance_scale":  st.session_state.guidance_scale,
                    "num_images_per_prompt":  st.session_state.num_inference,
                    "num_inference_steps":  st.session_state.inference_step,
                    "size":  st.session_state.output_size
                }
            elif generate:
                data = {
                    "prompt": st.session_state.prompt ,
                    "model": st.session_state.image_style,
                    "guidance_scale":  st.session_state.guidance_scale,
                    "num_images_per_prompt":  st.session_state.num_inference,
                    "num_inference_steps":  st.session_state.inference_step,
                    "size":  st.session_state.output_size
                    }
            try:
                print(data)
            except Exception as e:
                st.warning("새로고침이 필요합니다. 새로고침 후 시도해주시기 바랍니다.")
            prompt = data["prompt"]
            num_images = int(data["num_images_per_prompt"])
            
            st.session_state.save_parameter = data
            # 리퀘스트를 보낼 URL
            start_time = time.time()
            with st.spinner("🔮 마법같은 능력으로 emoji 생성 중..."):
            
                if st.session_state.model_select == "한국어" :
                    response = requests.post(f"{st.secrets['url']}/kor_submit", json=data)
                else :
                    response = requests.post(f"{st.secrets['url']}/eng_submit", json=data)

                try:
                    image_byte_list = response.json()["images"]
                    remove_image_byte_list = response.json()["removes"]
                except Exception as e:
                    st.error(f"❌ 에러가 발생했습니다. 서버 상의 문제일 수 있습니다. 잠시 후 시도해주세요.")
                    st.stop()

                decode_image_list = [Image.open(io.BytesIO(base64.b64decode(image))) for image in image_byte_list ]
                remove_decode_image_list = [Image.open(io.BytesIO(base64.b64decode(image))) for image in remove_image_byte_list ]
            
                st.session_state['image_list'] = decode_image_list
                st.session_state['remove_bg_image_list'] = remove_decode_image_list
                
                st.session_state.submit = False
                st.session_state['remove_bg'] = False
            
            executed_time = time.time() - start_time
            per_emoji_time = executed_time / num_images
            with col3:
                st.success(f"🎉 생성 완료! Emoji 당 {per_emoji_time:.1f}초 소요 되었습니다.")

            # st.balloons()
                
        if st.session_state['image_list'] :
            with st.expander("사용한 프롬프트"):
                st.markdown(f"`{st.session_state.save_parameter['prompt']}`")
            # st.markdown("#### Generated Emoji's preview(s)")
            with st.expander("생성 된 Emoji", expanded=True):
                img_index = image_select(
                    label="",
                    images= st.session_state['image_list'],
                    use_container_width = 6,
                    return_value = "index" 
                )
                
                # st.markdown("#### Selected Emoji")

            # with st.container():
                # image_col1 , image_col2 = st.columns([4,2])
                # with image_col1 :
                st.markdown(
                    """
                    <style>
                        [data-testid=stImage]{
                            text-align: left;
                            display: block;
                            margin-left: auto;
                            margin-right: auto;
                            width: 80%;
                        }
                    </style>
                    """, unsafe_allow_html=True)
                if st.session_state["remove_bg"] :
                    st.image(st.session_state['remove_bg_image_list'][img_index], use_column_width="auto")
                    img = st.session_state['remove_bg_image_list'][img_index]
                else :
                    st.image(st.session_state['image_list'][img_index], use_column_width="auto")
                    img = st.session_state['image_list'][img_index]

                # with image_col2:
                # down_button, remove_bg = st.columns([1,1])
                # with down_button:
                buf = io.BytesIO()
                img.save(buf, format = "PNG")
                buf_img = buf.getvalue()

                remove_bg = st.checkbox("배경 제거 (beta)", value=False, key="remove_bg", help="뒷 배경을 제거합니다.")
                if remove_bg != st.session_state['remove_bg'] :
                    st.session_state['remove_bg'] = remove_bg
                    st.experimental_rerun()
                btn = st.download_button(
                    label="Download emoji",
                    data= buf_img,
                    file_name = f'{st.session_state.save_parameter["prompt"]}.png',
                    mime="image/png",
                    )
                if btn:
                    st.balloons()
                # st.markdown("###### 배경 제거 (beta)")
                # remove_bg = st.radio(" ", (False, True), label_visibility="collapsed")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("---")
        under_col1, under_col2 = st.columns([3,1])
        with under_col1:
            with st.expander("도대체 이게 뭘 하는 건가요? 🤔", expanded=True):
                st.markdown("Text-to-Emoji, 부제 Emoji Diffusion은 Text를 입력으로 받아 텍스트의 내용에 맞게 Emoji를 출력하는 프로젝트입니다. \
                    \n이 프로젝트는 [Latent Diffusion](https://arxiv.org/abs/2112.10752)을 기반으로 만들어졌으며, 각 Emoji의 데이터셋으로 fine tuned 된 모델을 사용하고 있습니다.")
            with st.expander("알겠어요. 그러면 어떻게 사용하면 되는거죠? 😐"):
                st.markdown("텍스트 입력란에 생성하고 싶은 Emoji의 내용을 입력하고, **Emoji 생성** 버튼을 누르면 됩니다.")
                st.markdown("딱히 생각나는 말이 없거나 텍스트를 입력하기 귀찮다면, **I'm Feeling Lucky** 버튼을 써서 예측할 수 없는 Emoji 생성의 바다로 떠나보세요.")
                st.markdown("마음에 드는 Emoji가 있으면, 다운로드 버튼을 눌러서 저장해보세요.")
            with st.expander("더 잘 사용할 수 있는 방법들 📝"):
                st.markdown("프롬프트를 작성할 때, 주저하지 말고 길고 자세히 적어보세요. 문장의 길이가 길어질수록 더 많은 정보를 얻을 수 있습니다.")
                st.markdown("배경 제거 기능은 아직 beta 버전이기 때문에, 정확도가 떨어질 수 있습니다.")
                st.markdown("Cfg scale factor는 모델이 얼마나 텍스트의 내용을 반영하는지를 결정하는 파라미터입니다. 25까지 설정 할 수 있지만, 15 이상의 값은 추천하지 않습니다.")
            with st.expander("Diffusion은 정말 신기한 것 같아요! 어디서 더 이런 것을 볼 수 있죠? 😗"):
                st.markdown("아래에 있는 링크를 통해 **Diffusion**에 대해 더 자세히 알아보세요.")
                st.markdown("[Stable Diffusion Huggingface spaces](https://huggingface.co/spaces/stabilityai/stable-diffusion)")
                st.markdown("[WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)")
                st.markdown("[Stable Diffusion 공식 디스코드](https://discord.com/invite/stablediffusion)")
                st.markdown("####")
                
if __name__ == "__main__" :
    main()
