import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Interfaz para definir la estructura de los datos del producto
export interface Products {
  id: number;
  nombre: string;
  precio: number;
}

@Injectable({
  providedIn: 'root',
})
export class Api {
  // Cliente http para realizar las consultas externas
  private http = inject(HttpClient);
  
  // URL de la API proporcionada por el instituto
  private apiUrl = 'https://fakestoreapi.com/products';

  /**
   * MÉTODO GET: Obtener datos de la API
   */
  getProducts(): Observable<Products[]> {
    return this.http.get<Products[]>(this.apiUrl);
  }

  /**
   * MÉTODO POST: Crear un nuevo producto
   */
  createProduct(product: Products): Observable<Products> {
    return this.http.post<Products>(this.apiUrl, product);
  }

  /**
   * MÉTODO PUT: Reemplazar un recurso existente por completo
   */
  updateProductComplete(id: number, producto: Products): Observable<Products> {
    return this.http.put<Products>(`${this.apiUrl}/${id}`, producto);
  }

  /**
   * MÉTODO PATCH: Actualizar parcialmente un recurso
   */
  updatePproductPartial(id: number, cambios: Partial<Products>): Observable<Products> {
    return this.http.patch<Products>(`${this.apiUrl}/${id}`, cambios);
  }

  /**
   * MÉTODO DELETE: Eliminar un recurso
   */
  deleteProduct(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}