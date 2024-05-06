import service from '../server'

export const processUpload = (data) => {
    return service.post('/process/upload', data)
}
export const processByhand = (data) => {
    return service.post('/process/byhand', data)
}

