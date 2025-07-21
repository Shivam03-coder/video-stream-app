from ..module.auth.auth_router import auth_router

root_router = [{"prefix": "/auth", "router": auth_router}]
