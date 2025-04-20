import streamlit as st
import requests

st.title("SHL Assessment Recommender 💼🤖")
st.write("Enter a job role or hiring scenario, and get matching SHL assessments.")

query = st.text_area("Enter your query:", height=150)

if st.button("Get Recommendations"):
    if query.strip() == "":
        st.warning("Please enter a query.")
    else:
        try:
            response = requests.post("http://localhost:8000/recommend", json={"query": query})
            if response.status_code == 200:
                results = response.json()
                st.success(f"Top {len(results)} assessment(s) found:")

                for item in results:
                    st.markdown(f"### 🔗 [{item['description'][:50]}...]({item['url']})", unsafe_allow_html=True)
                    st.write(item["description"])
                    st.write(f"🕒 **Duration**: {item['duration']} mins")
                    st.write(f"🌍 **Remote Support**: {item['remote_support']}")
                    st.write(f"🧪 **Test Type**: {item['test_type']}")
                    st.markdown("---")
            else:
                st.error(f"Error {response.status_code}: {response.json()['detail']}")
        except Exception as e:
            st.error(f"Failed to fetch recommendations. Error: {e}")
