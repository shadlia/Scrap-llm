import streamlit as st
import asyncio
from logic.experiment_runner import add_to_dataset
from logic.utils import fill_form_from_json


def render_add_to_dataset_form():
    st.title("Add to Dataset 🏛️")
    st.markdown("Add new items to your experiment dataset")

    # Model selection and dataset name
    col1, col2 = st.columns(2)
    with col1:
        dataset_name = st.selectbox(
            "Dataset Name",
            [
                "extraction_dataset",
                "extraction_test_dataset",
                "extraction_train_dataset",
            ],
            key="dataset_name_key",
        )

    with col2:
        url = st.text_input("Product URL", placeholder="https://example.com/product")

    # Initialize JSON input value
    if "json_input_value" not in st.session_state:
        st.session_state["json_input_value"] = """{
    "variants": [
        {
            "url": "https://example.com/product",
            "product_name": "Example Product 1",
            "product_sku": "",
            "product_gtin": "",
            "product_public_price_ttc": "",
            "product_price_after_discount_ttc": "99.99",
            "product_option": "",
            "product_color": "",
            "product_size": "",
            "product_stock": "",
            "product_country_of_manufacture": "Country",
            "product_image_url": "https://example.com/image.jpg"
        }
    ]
}"""

    # Create two columns for form and JSON input
    form_col, json_col = st.columns(2)

    with form_col:
        st.subheader("Expected Output")
        # Create a form for adding items
        with st.form("add_to_dataset_form"):
            # Display form for each variant
            if "form_values" not in st.session_state:
                st.session_state.form_values = [
                    {
                        "name": "",
                        "product_public_price_ttc": "",
                        "product_price_after_discount_ttc": "",
                        "country": "",
                        "image_url": "",
                        "sku": "",
                        "gtin": "",
                        "option": "",
                        "color": "",
                        "size": "",
                        "stock": "",
                    }
                ]
            for i, variant in enumerate(st.session_state.form_values):
                st.markdown(f"### Variant {i + 1}")

                product_name = st.text_input(
                    "Product Name", value=variant["name"], key=f"name_{i}"
                )
                product_public_price_ttc = st.text_input(
                    "Product Public Price (TTC)",
                    value=variant.get("product_public_price_ttc", ""),
                    key=f"product_public_price_ttc_{i}",
                )
                product_price_after_discount_ttc = st.text_input(
                    "Product Price After Discount (TTC)",
                    value=variant.get("product_price_after_discount_ttc", ""),
                    key=f"product_price_after_discount_ttc_{i}",
                )
                product_country = st.text_input(
                    "Country of Manufacture",
                    value=variant["country"],
                    key=f"country_{i}",
                )
                product_image_url = st.text_input(
                    "Product Image URL",
                    value=variant["image_url"],
                    key=f"image_url_{i}",
                )
                print(
                    product_name,
                    product_public_price_ttc,
                    product_price_after_discount_ttc,
                    product_country,
                    product_image_url,
                )

                col1, col2 = st.columns(2)
                with col1:
                    product_sku = st.text_input(
                        "SKU", value=variant["sku"], key=f"sku_{i}"
                    )
                    product_gtin = st.text_input(
                        "GTIN", value=variant["gtin"], key=f"gtin_{i}"
                    )
                    product_option = st.text_input(
                        "Option", value=variant["option"], key=f"option_{i}"
                    )
                with col2:
                    product_color = st.text_input(
                        "Color", value=variant["color"], key=f"color_{i}"
                    )
                    product_size = st.text_input(
                        "Size", value=variant["size"], key=f"size_{i}"
                    )
                    product_stock = st.text_input(
                        "Stock", value=variant["stock"], key=f"stock_{i}"
                    )

                print(
                    product_sku,
                    product_gtin,
                    product_option,
                    product_color,
                    product_size,
                    product_stock,
                )

                st.markdown("---")

            # Submit button
            submitted = st.form_submit_button("Add to Dataset")

            if submitted:
                try:
                    all_variants_details_from_form = []
                    for i in range(len(st.session_state.form_values)):
                        product_details = {
                            "name": st.session_state.get(f"name_{i}", ""),
                            "product_public_price_ttc": st.session_state.get(
                                f"product_public_price_ttc_{i}", ""
                            ),
                            "product_price_after_discount_ttc": st.session_state.get(
                                f"product_price_after_discount_ttc_{i}", ""
                            ),
                            "country": st.session_state.get(f"country_{i}", ""),
                            "image_url": st.session_state.get(f"image_url_{i}", ""),
                            "sku": st.session_state.get(f"sku_{i}", ""),
                            "gtin": st.session_state.get(f"gtin_{i}", ""),
                            "option": st.session_state.get(f"option_{i}", ""),
                            "color": st.session_state.get(f"color_{i}", ""),
                            "size": st.session_state.get(f"size_{i}", ""),
                            "stock": st.session_state.get(f"stock_{i}", ""),
                        }
                        all_variants_details_from_form.append(product_details)

                    if all_variants_details_from_form:
                        asyncio.run(
                            add_to_dataset(
                                dataset_name, url, all_variants_details_from_form
                            )
                        )
                        num_variants_added = len(all_variants_details_from_form)
                        st.success(
                            f"Item with {num_variants_added} variant(s) added to dataset '{dataset_name}' successfully!"
                        )
                    else:
                        st.warning("No variant details provided in the form to add.")
                except Exception as e:
                    st.error(f"Error adding item to dataset: {str(e)}")

    with json_col:
        st.subheader("JSON Input")
        json_input = st.text_area(
            "Paste your JSON here",
            height=400,
            value=st.session_state["json_input_value"],
            key="json_input_area_key",
        )
        st.session_state["json_input_value"] = json_input

        if st.button("Fill Form from JSON"):
            variants = fill_form_from_json(json_input)
            if variants:
                st.session_state.form_values = variants
                st.success(
                    f"Form values updated for {len(variants)} variants! Click 'Add to Dataset' to submit."
                )
                st.rerun()
