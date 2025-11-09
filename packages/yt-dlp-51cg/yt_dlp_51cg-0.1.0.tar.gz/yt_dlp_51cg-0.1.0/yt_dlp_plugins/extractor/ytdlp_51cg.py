import base64
from typing import Dict, List, Optional, Tuple
from urllib.parse import unquote_to_bytes

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp import YoutubeDL
from yt_dlp.utils import ExtractorError, replace_extension


class FiftyOneCgArchiveIE(InfoExtractor):
    """Extractor for https://51cg1.com archive pages."""

    _VALID_URL = r"https?://(?:www\.)?51cg1\.com/archives/(?P<id>\d+)/?"
    _TESTS = [
        {
            "url": "https://51cg1.com/archives/234404/",
            "info_dict": {
                "id": "234404",
                "title": "md5:3d630a60c1b3e41a2fb864e3d454e3ac",
            },
            "params": {"skip_download": True},
        }
    ]

    _USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0"
    )
    _LAZYLOAD_DELAY_MS = 4000
    _INLINE_WAIT_MS = 8000

    _CLEANUP_SCRIPT = """
        el => {
            const selectors = [
                'div.txt-apps',
                'div.dplayer',
                'div.table-responsive',
                'p.content-copyright',
                'div.content-tabs',
                'div.btn-download',
                'blockquote'
            ];
            selectors.forEach(sel => {
                el.querySelectorAll(sel).forEach(node => node.remove());
            });
        }
    """

    _DESCRIPTION_BLACKLIST = [
        "热门吃瓜",
        (
            "版权声明：本文著作权归 51吃瓜网所有， 任何媒体、网站或个人未经授权不得复制、转载、摘编或以其他方式使用， "
            "否则将依法追究其法律责任。"
        ),
    ]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        m3u8_url = None
        cleanup_description = ""
        thumbnails: List[Dict[str, str]] = []
        title = None

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                context = browser.new_context(user_agent=self._USER_AGENT)
                context.add_cookies(
                    [
                        {
                            "name": "user-choose",
                            "value": "true",
                            "domain": ".51cg1.com",
                            "path": "/",
                        }
                    ]
                )
                page = context.new_page()

                def _maybe_capture_request(request):
                    nonlocal m3u8_url
                    req_url = request.url
                    if ".m3u8" in req_url and not m3u8_url:
                        m3u8_url = req_url

                page.on("request", _maybe_capture_request)
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=45000)
                except PlaywrightTimeoutError:
                    self.report_warning(
                        "Initial navigation timed out; continuing with partial content"
                    )

                try:
                    page.wait_for_selector("h1.post-title", timeout=30000)
                except PlaywrightTimeoutError as exc:
                    raise ExtractorError(
                        "Failed to load article content (title selector missing)",
                        expected=True,
                    ) from exc

                # Lazy-loaded images require scrolling to trigger data-src replacements.
                try:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(self._LAZYLOAD_DELAY_MS)
                except PlaywrightTimeoutError:
                    self.report_warning(
                        "Scrolling delay expired before all images loaded"
                    )
                except Exception:
                    pass

                inline_ready_script = """
                    contentSel => {
                        const container = document.querySelector(contentSel);
                        if (!container) {
                            return false;
                        }
                        const imgs = Array.from(container.querySelectorAll('img'));
                        if (!imgs.length) {
                            return false;
                        }
                        return imgs.every(img => {
                            const val = img.getAttribute('src') || img.getAttribute('data-src') || img.getAttribute('data-original');
                            return val && val.startsWith('data:');
                        });
                    }
                """
                try:
                    page.wait_for_function(
                        inline_ready_script,
                        timeout=self._INLINE_WAIT_MS,
                        arg='div.post-content[itemprop="articleBody"]',
                    )
                except PlaywrightTimeoutError:
                    self.report_warning(
                        "Inline thumbnails did not finish loading; falling back to current state"
                    )

                title = page.locator("h1.post-title").inner_text().strip()
                content = page.locator('div.post-content[itemprop="articleBody"]')
                content.evaluate(self._CLEANUP_SCRIPT)
                cleanup_description = self._sanitize_description(
                    content.inner_text().strip(), url
                )
                raw_imgs = content.locator("img").evaluate_all(
                    "els => els.map(el => el.getAttribute('src') || el.getAttribute('data-src') || el.getAttribute('data-original'))"
                )
                thumbnails, inline_thumbs = self._build_inline_thumbnails(raw_imgs)
            finally:
                browser.close()

        if not m3u8_url:
            raise ExtractorError(
                "Failed to locate HLS playlist (.m3u8) while scraping the page",
                expected=True,
            )

        http_headers = {
            "Origin": "https://51cg1.com",
            "Referer": url,
            "User-Agent": self._USER_AGENT,
        }

        return {
            "id": video_id,
            "title": title,
            "description": cleanup_description or None,
            "thumbnails": thumbnails,
            "url": m3u8_url,
            "protocol": "m3u8_native",
            "http_headers": http_headers,
            "_inline_thumbnails": inline_thumbs,
            "thumbnail": self._pick_primary_thumbnail(thumbnails, inline_thumbs),
        }

    def _sanitize_description(self, text: str, source_url: str) -> Optional[str]:
        cleaned = text or ""
        for forbidden in self._DESCRIPTION_BLACKLIST:
            cleaned = cleaned.replace(forbidden, "")
        cleaned = cleaned.strip()

        if not cleaned and not source_url:
            return None

        if source_url:
            if cleaned:
                cleaned = f"{cleaned}\n\nSource: {source_url}"
            else:
                cleaned = f"Source: {source_url}"
        return cleaned or None

    def _build_inline_thumbnails(
        self, img_srcs: List[Optional[str]]
    ) -> Tuple[Optional[List[Dict[str, str]]], List[Dict[str, object]]]:
        inline_public: List[Dict[str, str]] = []
        inline_payloads: List[Dict[str, object]] = []

        for idx, raw_src in enumerate(img_srcs or []):
            if not raw_src:
                continue
            src = raw_src.strip()
            if not src or not src.startswith("data:"):
                continue
            normalized = self._normalize_data_url(src)
            payload, mime, ext = self._decode_data_url(normalized)
            thumb_id = f"inline-{idx}"
            inline_public.append(
                {
                    "id": thumb_id,
                    "url": normalized,
                    "ext": ext,
                }
            )
            inline_payloads.append(
                {
                    "id": thumb_id,
                    "data": payload,
                    "ext": ext,
                    "mime": mime,
                    "data_url": normalized,
                }
            )

        return inline_public or None, inline_payloads

    def _normalize_data_url(self, data_url: str) -> str:
        prefix, _, payload = data_url.partition(",")
        if ";base64" in prefix.lower() or not payload:
            return data_url

        raw_bytes = unquote_to_bytes(payload)
        b64 = base64.b64encode(raw_bytes).decode("ascii")
        return f"{prefix};base64,{b64}"

    def _decode_data_url(self, data_url: str):
        header, _, payload = data_url.partition(",")
        meta = header[5:] if header.startswith("data:") else "image/jpeg"
        parts = meta.split(";")
        mime = parts[0] if "/" in parts[0] else "application/octet-stream"
        ext = self._ext_from_mime(mime)
        is_base64 = any(p.lower() == "base64" for p in parts[1:])
        data = base64.b64decode(payload) if is_base64 else unquote_to_bytes(payload)
        return data, mime, ext

    def _ext_from_mime(self, mime: str) -> str:
        mapping = {
            "image/jpeg": "jpg",
            "image/jpg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
            "image/bmp": "bmp",
            "image/svg+xml": "svg",
        }
        return mapping.get(mime.lower(), "jpg")

    def _pick_primary_thumbnail(
        self,
        inline_public: Optional[List[Dict[str, str]]],
        inline_thumbs: List[Dict[str, object]],
    ) -> Optional[str]:
        if inline_public:
            return inline_public[-1]["url"]
        if inline_thumbs:
            return inline_thumbs[-1]["data_url"]
        return None


def _patch_inline_thumbnail_writer():
    if getattr(YoutubeDL, "_yt_dlp_51cg_inline_patch", False):
        return

    original = YoutubeDL._write_thumbnails

    def _write_thumbnails_with_inline(
        self, label, info_dict, filename, thumb_filename_base=None
    ):
        result = original(self, label, info_dict, filename, thumb_filename_base)

        inline_thumbs = info_dict.pop("_inline_thumbnails", None)
        if not inline_thumbs:
            return result

        write_all = self.params.get("write_all_thumbnails", False)
        write_any = write_all or self.params.get("writethumbnail", False)
        if not write_any:
            return result

        if not filename:
            return result

        if thumb_filename_base is None:
            thumb_filename_base = filename

        if not self._ensure_dir_exists(filename):
            return None

        processed = [] if result is None else list(result)
        multiple = write_all and len(inline_thumbs) > 1
        iterator = inline_thumbs if write_all else inline_thumbs[-1:]

        for thumb in reversed(iterator):
            ext = thumb.get("ext") or "jpg"
            thumb_id = thumb.get("id") or "inline"
            suffix = f"{thumb_id}.{ext}" if multiple else ext
            interim_path = replace_extension(filename, suffix, info_dict.get("ext"))
            final_path = replace_extension(
                thumb_filename_base, suffix, info_dict.get("ext")
            )

            existing = self.existing_file((final_path, interim_path))
            if existing:
                thumb_path = existing
            else:
                try:
                    with open(interim_path, "wb") as out:
                        out.write(thumb["data"])
                    thumb_path = interim_path
                except OSError as err:
                    self.report_warning(
                        f"Unable to write inline thumbnail {thumb_id}: {err}"
                    )
                    continue

            thumb_record = {
                "id": thumb_id,
                "filepath": thumb_path,
                "ext": ext,
                "url": thumb.get("data_url"),
            }
            thumb.pop("data", None)
            info_dict.setdefault("thumbnails", []).append(
                {k: v for k, v in thumb_record.items() if v is not None}
            )
            processed.append((thumb_path, final_path))
            if processed and not write_all:
                break

        return processed

    YoutubeDL._write_thumbnails = _write_thumbnails_with_inline
    YoutubeDL._yt_dlp_51cg_inline_patch = True


_patch_inline_thumbnail_writer()
