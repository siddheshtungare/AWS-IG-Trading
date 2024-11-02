Current folder structure

AWS-IG-TRADING/
├── .aws-sam/
│ ├── build/
│ ├── cache/
│ ├── deps/
│ └── build.toml
├── Docos-IG-Trading/
├── functions/
│ ├── events/
│ │ ├── error_event_ig_run_strategy.json
│ │ ├── event_ig_buy.json
│ │ ├── event_ig_sell.json
│ │ ├── event.json
│ │ ├── ig_run_strategy_fibo.json
│ │ ├── ig_run_strategy_ml.json
│ │ └── ig_run_strategy_sma.json
│ ├── ig_login/
│ │ ├── **init**.py
│ │ ├── app.py
│ │ ├── ig_api_helper.py
│ │ └── requirements.txt
│ ├── ig_process_buy_sell/
│ │ ├── **init**.py
│ │ ├── app.py
│ │ ├── ig_api_helper.py
│ │ ├── requirements.txt
│ │ └── util_funcs.py
│ ├── ig_run_strategy/
│ │ ├── **init**.py
│ │ ├── app.py
│ │ ├── ig_api_helper.py
│ │ ├── requirements.txt
│ │ ├── strategies/
│ │ │ ├── **init**.py
│ │ │ ├── fibo_strategy.py
│ │ │ ├── ml_strategy.py
│ │ │ └── sma_strategy.py
│ │ └── util_funcs.py
│ └── sagemaker_endpoint/
│ ├── **init**.py
│ ├── inference.py
│ ├── requirements.txt
│ └── model/
│ ├── **init**.py
│ ├── requirements.txt
│ └── code/
│ ├── **init**.py
│ └── inference.py
├── Images/
├── layers/
├── scripts/
│ └── clean_layer.py
├── statemachine/
│ └── ig_trader.asl.json
├── **init**.py
├── .env
├── .gitattributes
├── .gitignore
├── README-old.md
├── README.md
├── samconfig.toml
├── sample-template.yaml
└── template.yaml
