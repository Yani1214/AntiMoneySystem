import service from '../server'

export const analysisDetection = (data) => {
    return service.post('/v1/analysis/', data)
}

export const analysisTrace = (data) => {
    return service.post('/v1/analysis/trace', data)
}