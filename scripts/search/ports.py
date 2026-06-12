from scripts.searching import Search
from commons import BASE_URL, encode
from flask import redirect

def get_port_inner(call: str, query: int):
    return redirect(f"{BASE_URL}/change-port/{query}")

get_port = Search(r"self.(?P<query>[0-9]+)", get_port_inner)

def parse_port_inner(call: str, query: str):
    return get_port(f"self.{encode(query)}")

parse_port = Search(r"self.(?P<query>[a-z_]+)", parse_port_inner)