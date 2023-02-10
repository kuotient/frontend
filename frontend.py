import streamlit as st
import io
import base64
import random
import requests
import streamlit_nested_layout
from streamlit_image_select import image_select
import os
import time

from PIL import Image
from rembg import remove

# st.set_page_config(page_title="Text-to-Emoji", layout="wide", page_icon="😊")
st.set_page_config(page_title="Text-to-Emoji", layout="wide", page_icon="🔮")
st.image("small_logo.png")
st.sidebar.title("Text-to-Emoji 😊")
st.sidebar.caption("프롬프트를 입력해 Emoji를 생성하세요!.")
st.sidebar.markdown("Made by team [WE-FUSION](https://github.com/boostcampaitech4lv23nlp2/final-project-level2-nlp-11)")
st.sidebar.header("Settings 🔧")

# toggle = st.sidebar.checkbox("Toggle Update", value=True, help="Continuously update the pallete with every change in the app.")
# palette_size = int(st.sidebar.number_input("palette size", min_value=1, max_value=20, value=5, step=1, help="Number of colors to infer from the image."))
# sample_size = int(st.sidebar.number_input("sample size", min_value=5, max_value=3000, value=500, step=500, help="Number of sample pixels to pick from the image."))
# seed = int(st.sidebar.number_input("random seed", value=42, help="Seed used for all random samplings."))

def main():
    left, right = st.columns([4, 1])

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
    
    with left :
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
        st.markdown("---")    
        st.text_area(
            label= "Input Text(Prompt)",
            placeholder = "A cute rabbit",
            value = st.session_state.prompt,
            key="prompt",
            max_chars=75,
            help="프롬프트를 입력해주세요. 최대 75자까지 입력 가능합니다."
            # label_visibility="collapsed",
        )
        # co3, col1, col2, col4 = st.columns([2,1,1,2])
        col1, col2, col3 = st.columns([1,1,4])
        with col1:
            generate = st.button(label="Generate Emoji", type="primary")
            if generate:
                st.session_state.submit = True
            
        with col2:
            with open("prompt.txt") as f:
                sample_prompts = f.read().splitlines()
                
            feeling_lucky = st.button(label="I'm Feeling lucky", type="secondary",)
            if feeling_lucky:
                lucky_prompt = random.choice(sample_prompts)
                # print(lucky_prompt)
                st.session_state.submit = True
        
        if st.session_state.submit:
            if feeling_lucky:
                data = {
                    "prompt": lucky_prompt,
                    "guidance_scale":  st.session_state.guidance_scale,
                    "num_images_per_prompt":  st.session_state.num_inference,
                    "num_inference_steps":  st.session_state.inference_step,
                    "size":  st.session_state.output_size
                }
            elif generate:
                data = {
                    "prompt": st.session_state.prompt ,
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
            with st.spinner("🔮 마법같은 능력으로 이모지 생성 중..."):
            
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
            st.success(f"🎉 이모지 생성 완료! 이모지 당 {per_emoji_time:.2f}초 밖에 소요하지 않았습니다!")
            st.markdown("사용 된 프롬프트")
            st.markdown(f"`{prompt}`")
            st.markdown("---")
            # st.balloons()
                
        if st.session_state['image_list'] :
            
            st.markdown("#### Generated Emoji's preview(s) of:")
            img_index = image_select(
                label="",
                images= st.session_state['image_list'],
                use_container_width = 8,
                return_value = "index" 
            )
            
            st.markdown("#### Select Emoji")

            with st.container() :
                image_col1 , image_col2 = st.columns([4,1])
                with image_col1 :
                    st.markdown(
                        """
                        <style>
                            [data-testid=stImage]{
                                text-align: center;
                                display: block;
                                margin-left: auto;
                                margin-right: auto;
                                width: 100%;
                            }
                        </style>
                        """, unsafe_allow_html=True)
                    if st.session_state["remove_bg"] :
                        st.image(st.session_state['remove_bg_image_list'][img_index], use_column_width="auto")
                        img = st.session_state['remove_bg_image_list'][img_index]
                    else :
                        st.image(st.session_state['image_list'][img_index], use_column_width="auto")
                        img = st.session_state['image_list'][img_index]
    
                with image_col2 :
                    buf = io.BytesIO()
                    img.save(buf, format = "PNG")
                    buf_img = buf.getvalue()

                    btn = st.download_button(
                        label="Download image",
                        data= buf_img,
                        file_name = 'generated_image.png',
                        mime="image/png",
                        )
                    
                    st.markdown("##")
                    st.markdown("###### 배경 제거 (beta)")
                    remove_bg = st.radio(" ", (False, True), label_visibility="collapsed")
                    if remove_bg != st.session_state['remove_bg'] :
                        st.session_state['remove_bg'] = remove_bg
                        st.experimental_rerun()



    # with right :

    # st.sidebar.markdown("언어 선택")
    model_select = st.sidebar.radio(
        "언어 선택",
        ("English",
        "한국어",),
        help="한국어 모델은 현재 개발중입니다."
    )
    # st.sidebar.markdown("이모지 스타일")
    image_style = st.sidebar.selectbox(
        "이모지 스타일",
        ("open-emoji","noto-emoji"),
        help="특정 스타일의 이모지를 생성할 수 있습니다."
    )
    
    # st.sidebar.markdown("이모지 아웃풋 크기")
    output_option = st.sidebar.selectbox(
        "이모지 아웃풋 크기",
        ("512","256","128"),
        help = "이모지의 출력 크기를 선택할 수 있습니다."
    )

    # st.sidebar.markdown("Number of outputs")
    num_inference = st.sidebar.slider("생성할 이모지 갯수",1,4,3,help="생성할 이모지의 개수를 선택할 수 있습니다.")

    # st.sidebar.markdown("cfg scale")
    guidance_scale = st.sidebar.slider("Cfg scale",0, 25, 7,help="이모지가 prompt를 따라가는 정도를 조절할 수 있습니다.")


    st.session_state['model_select'] = model_select
    st.session_state['image_style'] = image_style
    st.session_state['output_size'] = int(output_option)
    st.session_state['num_inference'] = int(num_inference)
    st.session_state['guidance_scale'] = int(guidance_scale)
    st.session_state['inference_step'] = 30
    
if __name__ == "__main__" :
    main()
