# Approved historical photographs and document scans

This folder intentionally contains no photographs until an original scan has been
reviewed for identity, accuracy and reuse rights. This avoids substituting
representative photographs for real Beverage family records.

To publish a scan on the site:

1. Save the permitted JPG, PNG or WEBP inside this directory. For multi-page
   historical affidavits, save individual rendered pages with page numbers.
2. Add an entry to `data/media_manifest.json` using the **same exact**
   `item_identifier` as the existing Images and Maps inventory row's
   `Collection or item identifier` field:

   ```json
   {
     "item_identifier": "exact-archive-catalog-id",
     "local_path": "static/approved_media/example_scan_001.jpg",
     "rights_status": "permission",
     "credit": "Holding institution and creator as requested"
   }
   ```

3. Set `rights_status` only to `permission` or `public_domain`, based on
   documented authorization. Other values deliberately do not display locally.
4. Preserve source citations and date uncertainty in the corresponding archive
   inventory entry. Do not infer a photograph's exact capture date from the
   date of the historical event represented.
5. Verify the image, its caption, mobile presentation and source link in the
   GitHub pull-request preview before releasing.

The site also offers embedded previews of external archive pages when the
holding institution permits framing. External sites may block iframe display;
the original source link must always remain available.
