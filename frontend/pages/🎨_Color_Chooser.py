import streamlit as st
import cv2
import numpy as np
from uuid import uuid4
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
from detectron2 import model_zoo
from detectron2.utils.logger import setup_logger
from Homepage import get_session_state, set_session_state
import openai

setup_logger()



def get_session_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid4())
    if st.session_state.session_id not in st.session_state:
        st.session_state[st.session_state.session_id] = {}
    return st.session_state[st.session_state.session_id]

def set_session_state(state):
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid4())
    if st.session_state.session_id not in st.session_state:
        st.session_state[st.session_state.session_id] = {}
    st.session_state[st.session_state.session_id] = state

def is_user_logged_in():
    return get_session_state().get("is_logged_in", False)

def generate_openai_answer(prompt, api_key = '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'):
    openai.api_key = api_key
    model = 'gpt-3.5-turbo'  # You can change the model engine as needed

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "user", "content": prompt}
        ]
    )

    message = response['choices'][0]['message']['content'].strip()
    return message

if not is_user_logged_in():
    st.error("You need to log in to access this page.")
    st.stop()



st.title("House Wall Detection")
st.write("Upload an image to detect House Walls & ceilings.")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])

if uploaded_file is not None:
    image = np.array(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    dis_im = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    st.image(dis_im, caption='Uploaded Image.', use_column_width=True)

    # Save the uploaded image to session state
    st.session_state['original_image'] = dis_im


    # st.write("Applying Segmentation for Walls & ceilings...")
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml"))
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml")
    cfg.MODEL.DEVICE = 'cpu'
    predictor = DefaultPredictor(cfg)
    panoptic_seg, segments_info = predictor(image)["panoptic_seg"]
    v = Visualizer(image[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
    only_segmented_image_op = v.draw_panoptic_seg_predictions(panoptic_seg.to("cpu"), segments_info, alpha=0.01)

    choice_1 = st.sidebar.checkbox('wall', value=True)
    choice_2 = st.sidebar.checkbox('ceiling')
    if choice_1:
        choice = ['wall']
    if choice_2:
        choice = ['ceiling']
    if choice_1 and choice_2:
        choice = ['wall', 'ceiling']
    if not choice_1 and not choice_2:
        choice = "" 

    # make a radio choces multiple selectible with wall and ceiling 

    new_wall_color = st.sidebar.color_picker('Choose a wall color', '#FFFFFF', label_visibility="visible")
    # st.write(choice) 
    new_ceil_color = st.sidebar.color_picker('Choose a ceiling color', '#960B0B', label_visibility="visible")
    if 'wall' in choice and 'ceiling' in choice :
        b, g, r = tuple(int(new_wall_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        ceil_b , ceil_g, ceil_r = tuple(int(new_ceil_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        im = image
        panoptic_seg, segments_info = predictor(im)["panoptic_seg"]
        metadata = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])

        wall_index = -1
        for idx, item in enumerate(metadata.stuff_classes):
            if item == "wall":
                wall_index = idx
                break
        if wall_index != -1:
            metadata.stuff_colors[wall_index] = (r, g, b)
        # st.write("wall and ceiling both selected")
        ceiling_index = -1
        for idx, item in enumerate(metadata.stuff_classes):
            if item == "ceiling":
                ceiling_index = idx
                break
        if ceiling_index != -1:
            metadata.stuff_colors[ceiling_index] = (ceil_r, ceil_g, ceil_b)

        wall_segment_id = None
        for segment_info in segments_info:
            if segment_info["category_id"] == wall_index:
                wall_segment_id = segment_info["id"]
            if segment_info['category_id'] == ceiling_index:
                ceiling_segment_id = segment_info['id']

        if wall_segment_id is not None:
            wall_mask = (panoptic_seg == wall_segment_id).numpy()
            wall_color = (r, g, b)
            im[wall_mask] = wall_color
        
        if ceiling_segment_id is not None:
            ceiling_mask = (panoptic_seg == ceiling_segment_id).numpy()
            ceiling_color = (ceil_r, ceil_g, ceil_b)
            im[ceiling_mask] = ceiling_color
        masked_image = im[:, :, ::-1]
        st.image(im[:, :, ::-1], caption='Output (wall and ceiling both selected).', use_column_width=True)

    if 'wall' in choice and len(choice) == 1 :
        b, g, r = tuple(int(new_wall_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

        im = image
        panoptic_seg, segments_info = predictor(im)["panoptic_seg"]
        metadata = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])

        wall_index = -1
        for idx, item in enumerate(metadata.stuff_classes):
            if item == "wall":
                wall_index = idx
                break
        if wall_index != -1:
            metadata.stuff_colors[wall_index] = (r, g, b)

        wall_segment_id = None
        for segment_info in segments_info:
            if segment_info["category_id"] == wall_index:
                wall_segment_id = segment_info["id"]
                break

        if wall_segment_id is not None:
            wall_mask = (panoptic_seg == wall_segment_id).numpy()
            wall_color = (r, g, b)
            im[wall_mask] = wall_color
            masked_image = im[:, :, ::-1]
            st.image(im[:, :, ::-1], caption='Output (wall only).', use_column_width=True)


    if 'ceiling' in choice and len(choice) == 1 :
        # new_ceiling_color = st.sidebar.color_picker('Choose a color', '#FFFFFF')
        # b, g, r = tuple(int(new_wall_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        b, g, r = tuple(int(new_ceil_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        im = image
        panoptic_seg, segments_info = predictor(im)["panoptic_seg"]
        metadata = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])

        ceiling_index = -1
        for idx, item in enumerate(metadata.stuff_classes):
            if item == "ceiling":
                ceiling_index = idx
                break
        if ceiling_index != -1:
            metadata.stuff_colors[ceiling_index] = (r, g, b)

        ceiling_segment_id = None
        for segment_info in segments_info:
            if segment_info["category_id"] == ceiling_index:
                ceiling_segment_id = segment_info["id"]
                break

        if ceiling_segment_id is not None:
            ceiling_mask = (panoptic_seg == ceiling_segment_id).numpy()
            ceiling_color = (r, g, b)
            im[ceiling_mask] = ceiling_color
            masked_image = im[:, :, ::-1]
            st.image(im[:, :, ::-1], caption='Output (ceilig only).', use_column_width=True)

    if len(choice) == 0 and choice_1 == False and choice_2 == False:
        st.sidebar.warning("nothing selected Please select something")
    else:
        v = Visualizer(im[:, :, ::-1], metadata, scale=1.2)
        out = v.draw_panoptic_seg_predictions(panoptic_seg.to("cpu"), segments_info)
        prompt = f""" 
        These are some segmentations info generated from detectron2 model {segments_info} What suggestions can you give on color selection of wall and ceiling in 3 lines? 

        ---
        in output return in markdown format and bold the colors in output format output in more user pleasing way.
        Suggestion to user:
        """

        with st.expander("Show detected objects"):
            col1, col2 = st.columns(2)
            col1.image(out.get_image()[:, :, ::-1], caption='Output Image.', use_column_width=True)
            col2.image(only_segmented_image_op.get_image()[:, :, ::-1], caption='segmented image', use_column_width=True)
        
        suggestion_to_user = generate_openai_answer(prompt)
        st.markdown('### 💡Suggestion to user')
        st.warning(suggestion_to_user)
            

        if st.button('Download Image'):
            cv2.imwrite('output.jpg', out.get_image()[:, :, ::-1])
            st.write('Image downloaded')
    
# Check if the "Save Image" button is clicked
if st.button('Save Image'):
    # Write the masked image to disk
    cv2.imwrite('output.jpg', masked_image)
    
    # Save the output image in session
    st.session_state['output_image'] = masked_image
    
    # Display success message
    st.write('Image saved.')
