import requests
import json

def main():
    api_key = input("🔑 Please enter your API key: ").strip()
    url = f"http://api.qr-code-generator.com/v1/access-tokens?access-token={api_key}"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            tokens = data.get("items", data)

            print("\n✨ === Access Tokens === ✨")

            if isinstance(tokens, list) and tokens:
                for i, token_info in enumerate(tokens, start=1):
                    print(f"\n🔹 Token {i}")
                    print("──────────────────────────────")
                    print(f"🆔 ID:               {token_info.get('id', 'N/A')}")
                    print(f"🔐 Token:            {token_info.get('token', 'N/A')}")
                    print(f"📅 Created At:       {token_info.get('created_at', 'N/A')}")
                    print(f"✅ Enabled:          {token_info.get('enabled', 'N/A')}")
                    print(f"🚀 Rate Limit:       {token_info.get('rate_limit', 'N/A')}")
                    print(f"📈 Monthly Limit:    {token_info.get('rate_limit_month', 'N/A')}")
                    print(f"📊 Remaining:        {token_info.get('rate_number_month', 'N/A')}")
                print(f"\n🎯 Total tokens: {len(tokens)}")
            else:
                print("\n📦 Raw Response:")
                print(json.dumps(data, indent=4))

        else:
            print(f"❌ Error: Received status code {response.status_code}")
            print("🧾 Response body:", response.text)

    except requests.exceptions.RequestException as e:
        print("⚠️ An error occurred while making the request:", e)


if __name__ == "__main__":
    main()

