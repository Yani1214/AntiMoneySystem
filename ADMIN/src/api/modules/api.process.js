import service from '../server'

export const processUpload = (data) => {
    return service.post('/v1/process/upload', data)
}
export const processByhand = (data) => {
    return service.post('/v1/process/byhand', data)
}
export const processImport = (data) => {
    return service.post('/v1/process/byhand/import', data)
}
export const processExport = (data) => {
    return service.post('/v1/process/byhand/export', data)
}
export const processDetect = (data) => {
    return service.post('/v1/process/byhand/detect', data)
}
