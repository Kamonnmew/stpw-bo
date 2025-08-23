# # Simplified Automotive Parts Search - Deployment Guide

## ไฟล์ที่ใช้งานสำหรับระบบใหม่

### 📂 Configuration Files:
- `enhanced-skillset.json` - Skillset สำหรับวิเคราะห์รูปภาพเท่านั้น (3 skills)
- `simplified-index-schema.json` - Index schema ที่เหมาะสมกับรูปจริง (10 fields)
- `simplified-indexer.json` - Indexer configuration

### 🎯 ระบบที่ถูกปรับแต่งใหม่:
- **ไม่มี OCR** - เพราะรูปจริงไม่มี text
- **เน้น Visual Analysis** - objects, tags, description, colors
- **Vector Search** - ค้นหาด้วย image similarity
- **Semantic Search** - ค้นหาด้วยความหมาย

## ขั้นตอนการ Deploy

### 1. Deploy Simplified Index
```bash
curl -X PUT "https://auto-model-search.search.windows.net/indexes/simplified-automotive-parts-index?api-version=2023-11-01" \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_ADMIN_KEY" \
  -d @simplified-index-schema.json
```

### 2. Update Skillset  
```bash
curl -X PUT "https://auto-model-search.search.windows.net/skillsets/simplified-automotive-parts-skillset?api-version=2023-11-01" \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_ADMIN_KEY" \
  -d @enhanced-skillset.json
```

### 3. Deploy Indexer
```bash
curl -X PUT "https://auto-model-search.search.windows.net/indexers/simplified-automotive-indexer?api-version=2023-11-01" \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_ADMIN_KEY" \
  -d @simplified-indexer.json
```

## การทดสอบ

### Test Semantic Search
```bash
curl -X POST "https://auto-model-search.search.windows.net/indexes/simplified-automotive-parts-index/docs/search?api-version=2023-11-01" \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_QUERY_KEY" \
  -d '{
    "search": "brake part",
    "queryType": "semantic",
    "semanticConfiguration": "automotive-semantic-config",
    "top": 10
  }'
```

### Test Filter by Color
```bash
curl -X POST "https://auto-model-search.search.windows.net/indexes/simplified-automotive-parts-index/docs/search?api-version=2023-11-01" \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_QUERY_KEY" \
  -d '{
    "search": "*",
    "filter": "primaryColor eq 'black'",
    "top": 10
  }'
```

## หมายเหตุ
- ระบบนี้เหมาะสมกับรูปจริงที่ไม่มี text ให้ OCR
- เน้น visual analysis และ semantic search
- รองรับ vector search สำหรับความคล้ายกันของรูปภาพ