use axum::{Router, routing::get};
use tokio::net::TcpListener;

async fn health() -> &'static str {
    "ok"
}

fn app() -> Router {
    Router::new().route("/api/health", get(health))
}

#[tokio::main]
async fn main() {
    let listener = TcpListener::bind("127.0.0.1:8080").await.unwrap();
    println!("Aquarela listening on 127.0.0.1:8080");
    axum::serve(listener, app()).await.unwrap();
}

#[cfg(test)]
mod tests {

    use super::*;
    use axum::body::{Body, to_bytes};
    use axum::http::{Request, StatusCode};
    use tower::ServiceExt;

    #[tokio::test]
    async fn health_responde_ok() {
        let request = Request::get("/api/health").body(Body::empty()).unwrap();

        let response = app().oneshot(request).await.unwrap();

        assert_eq!(response.status(), StatusCode::OK);

        let body = to_bytes(response.into_body(), usize::MAX).await.unwrap();

        assert_eq!(&body[..], b"ok");
    }
}
