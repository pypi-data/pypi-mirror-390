def test():
    for folder in folders_with_deals:
        deal_id = folder.metadata.get("pipedrive", {}).get("deal_id")
        if not deal_id:
            continue
        print(f"\n🔍 Processing folder {folder.folder_number} (Deal ID: {deal_id})")
        current_products = pipedrive_service._make_request("GET", f"deals/{deal_id}/products")
        if current_products and current_products.get("data"):
            print(f"  ⏭️ Deal {deal_id} already has {len(current_products['data'])} products, skipping")
            continue
        products_to_attach = adapter.determine_products_for_folder(folder, pipedrive_service)
        if products_to_attach:
            print(f"  📦 Found {len(products_to_attach)} products to attach")
            result = pipedrive_service.attach_multiple_products_to_deal(deal_id, products_to_attach)
            print(f"  ✅ Attached {result['success_count']} products, {result['failure_count']} failed")
            if result['success_count'] > 0:
                if "pipedrive" not in folder.metadata:
                    folder.metadata["pipedrive"] = {}
                folder.metadata["pipedrive"]["products_attached"] = result["success_count"]
                folder.metadata["pipedrive"]["products_failed"] = result["failure_count"]
                folder.save(update_fields=["metadata"])
        else:
            print(f"  ❌ No products determined for folder {folder.folder_number}")
