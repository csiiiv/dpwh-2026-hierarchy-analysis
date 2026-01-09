const parquet = require('parquetjs-lite');
const fs = require('fs');

async function convertParquetToJson() {
    const parquetPath = '/home/temp/_CODE/DPWH_2026_GAA/data/FY 2026_DPWH DETAILS ENROLLED COPY (Final)_leaf_nodes.parquet';
    const outputPath = '/home/temp/_CODE/DPWH_2026_GAA/data/leaf_nodes.json';

    console.log('Reading parquet file...');
    const reader = await parquet.ParquetReader.openFile(parquetPath);
    
    const cursor = reader.getCursor();
    let record = null;
    const records = [];
    
    while (record = await cursor.next()) {
        records.push(record);
    }
    
    await reader.close();
    
    console.log(`Writing ${records.length} records to JSON...`);
    fs.writeFileSync(outputPath, JSON.stringify(records, null, 2));
    console.log('Done!');
}

convertParquetToJson().catch(console.error);
